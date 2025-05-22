import pytest
from app import app, db
from models import User
import bcrypt

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # si tu utilises Flask-WTF (sinon à enlever)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Création d'un utilisateur pour le test
            password = bcrypt.hashpw(b"correctpassword", bcrypt.gensalt())
            user = User(email="existant@example.com", password=password)
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_login_with_wrong_password(client):
    response = client.post('/login', data={
        'email': 'existant@example.com',
        'password': 'wrongpassword',
        'confirm_password': 'wrongpassword'  # doit correspondre à password pour éviter 400
    }, follow_redirects=True)

    # On vérifie que la réponse contient bien le message d'erreur attendu
    assert b'Email ou mot de passe incorrect' in response.data
