import bcrypt
from models import User, db

def test_admin_access_control(app, client):
    with app.app_context():
        # Création et ajout user admin
        hashed_pw = bcrypt.hashpw(b'test123', bcrypt.gensalt())
        admin_user = User(email='admin@test.com', password=hashed_pw, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()

        # On récupère l'id (obligatoire pour Flask-Login)
        admin_id = admin_user.id

    # Connexion via session client Flask-Login
    with client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_id)  # stocke l'id en string

        # Test accès admin
        response = client.get('/admin')
        assert response.status_code == 200
