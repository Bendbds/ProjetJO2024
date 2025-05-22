import json
import pytest
from app import db
from models import User, Event, CartItem
import bcrypt

@pytest.fixture
def logged_in_client(client, app):
    password = 'testpass'
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with app.app_context():
        user = User(email='user@test.com', password=pw_hash)
        db.session.add(user)
        db.session.commit()

        event = Event(name='Test Event', date='2025-05-21', price=10.0, stock=5)
        db.session.add(event)
        db.session.commit()

        user = User.query.get(user.id)
        event = Event.query.get(event.id)

    client.post('/login', data={
        'email': user.email,
        'password': password,
        'confirm_password': password
    }, follow_redirects=True)

    yield client, user, event

def test_add_to_cart(logged_in_client):
    client, user, event = logged_in_client

    response = client.post('/add_to_cart', 
        data=json.dumps({
            "title": event.name,
            "price": event.price,
            "event_id": event.id
        }),
        content_type='application/json'
    )
    assert response.status_code == 200

    response_json = response.get_json()
    assert response_json.get("message") == "Ajouté au panier !"

    with client.application.app_context():
        # Refresh user and event objects with new SQLAlchemy 2.0 style
        user = db.session.get(User, user.id)
        event = db.session.get(Event, event.id)

        cart_items = CartItem.query.filter_by(user_id=user.id).all()
        assert len(cart_items) == 1
        assert cart_items[0].offer_name == event.name
