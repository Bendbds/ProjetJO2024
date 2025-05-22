import bcrypt
from app import db
from models import User

import pytest

@pytest.fixture
def logged_user(client, app):
    password = bcrypt.hashpw(b"password", bcrypt.gensalt())
    user = User(email="cartuser@example.com", password=password)
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    return user

def test_add_to_cart(client, logged_user):
    # Utilise logged_user pour tester l'ajout au panier
    response = client.post('/add_to_cart', data={
        'event_id': 1,
        'quantity': 1
    }, follow_redirects=True)
    assert response.status_code == 200
