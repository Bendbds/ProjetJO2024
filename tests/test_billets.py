import bcrypt
from datetime import datetime
from app import app, db
from models import User, Event, Ticket

def test_view_billets(client):
    with app.app_context():
        # Création d'un utilisateur
        password = bcrypt.hashpw(b"password", bcrypt.gensalt())
        user = User(email="ticketuser@example.com", password=password)
        db.session.add(user)

        # Création d'un événement avec price (champ obligatoire)
        event = Event(name="Test Event", date=datetime.utcnow(), price=10.0, stock=10)
        db.session.add(event)
        db.session.commit()

        # Création d'un ticket lié à cet utilisateur et à cet événement
        ticket = Ticket(user_id=user.id, event_id=event.id, barcode_value="ABC123", created_at=datetime.utcnow())
        db.session.add(ticket)
        db.session.commit()

    # Connexion (POST avec confirm_password obligatoire)
    response = client.post('/login', data={
        'email': 'ticketuser@example.com',
        'password': 'password',
        'confirm_password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    # On vérifie que la réponse contient la valeur du ticket
    response = client.get('/mes_billets')
    assert b"ABC123" in response.data
