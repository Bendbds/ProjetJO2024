import pytest
from flask import url_for
from unittest.mock import patch

def test_create_checkout_session(logged_in_client):
    client, user, event = logged_in_client

    # Ajouter un item au panier en DB lié à user
    from models import CartItem, db
    cart_item = CartItem(offer_name=event.name, price=event.price, user_id=user.id, event_id=event.id)
    db.session.add(cart_item)
    db.session.commit()

    # Patch stripe.checkout.Session.create pour éviter appel réel Stripe
    with patch('app.stripe.checkout.Session.create') as mock_stripe_create:
        mock_stripe_create.return_value.url = "http://fake-stripe-checkout-url"
        
        response = client.post('/create-checkout-session', follow_redirects=False)
        assert response.status_code == 303
        assert "http://fake-stripe-checkout-url" in response.headers['Location']

    # Nettoyer la DB (optionnel)
    db.session.delete(cart_item)
    db.session.commit()

def test_create_checkout_session_empty_cart(logged_in_client):
    client, user, _ = logged_in_client

    # S'assurer que panier est vide pour cet utilisateur
    from models import CartItem, db
    CartItem.query.filter_by(user_id=user.id).delete()
    db.session.commit()

    response = client.post('/create-checkout-session', follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Votre panier est vide." in html
