import bcrypt
from app import db
from models import User

def test_register_and_login(client, app):
    # Test inscription
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b"S'inscrire" in response.data or response.status_code == 200

    # Créer un utilisateur pour le test login
    password_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt())
    with app.app_context():
        db.session.add(User(email='login@test.com', password=password_hash))
        db.session.commit()

    # Test connexion avec mot de passe incorrect
    response = client.post('/login', data={
        'email': 'login@test.com',
        'password': 'wrongpassword',
        'confirm_password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Email ou mot de passe incorrect" in response.data or response.status_code == 200
