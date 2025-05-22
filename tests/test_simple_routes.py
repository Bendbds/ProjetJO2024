import pytest
from app import app, db
from models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # si tu utilises WTForms
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # créer les tables en test
            yield client
            db.session.remove()
            db.drop_all()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Events' in response_text or 'Événement' in response_text

def test_register_get(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Inscription' in response.data or b'Email' in response.data

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Connexion' in response.data or b'Email' in response.data

def test_panier_get(client):
    response = client.get('/panier')
    assert response.status_code == 200
    # Panier vide, vérifie présence mot "Panier" dans la page
    assert b'Panier' in response.data or b'Votre panier' in response.data
