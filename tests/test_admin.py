import bcrypt
from models import User
from app import db

def test_admin_access(client, app):
    # User non admin (pas connecté)
    response = client.get('/admin')
    assert response.status_code == 302  # redirection vers login

    with app.app_context():
        admin_user = User(email='admin@test.com', password=bcrypt.hashpw(b'adminpass', bcrypt.gensalt()), is_admin=True)
        db.session.add(admin_user)
        db.session.commit()