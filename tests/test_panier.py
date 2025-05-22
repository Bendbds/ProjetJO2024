from models import User, Event, CartItem
import json

def test_panier_page(logged_in_client, app):
    client, user, event = logged_in_client

    # Ajouter un article au panier (avec offer_name et event_id)
    response_add = client.post('/add_to_cart',
        data=json.dumps({
            "offer_name": event.name,   # <- ici offer_name
            "price": event.price,
            "event_id": event.id
        }),
        content_type='application/json',
        follow_redirects=True
    )
    assert response_add.status_code == 200

    # Vérifier que l'item a bien été ajouté en base pour cet utilisateur
    with app.app_context():
        items = CartItem.query.filter_by(user_id=user.id).all()
        assert len(items) == 1
        assert items[0].offer_name == event.name

    # Récupérer la page panier
    response = client.get('/panier', follow_redirects=True)
    assert response.status_code == 200

    html = response.data.decode('utf-8')

    # Vérifier que le nom de l'événement est bien affiché dans la page
    assert event.name in html
