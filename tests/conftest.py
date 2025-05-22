import sys
import os
import pytest
import bcrypt
from datetime import datetime
from flask_login import login_user

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from models import User, Event

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SERVER_NAME'] = 'localhost.localdomain'  
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SECRET_KEY'] = 'test_secret_key'
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged_in_client(app, client):
    with app.app_context():
        hashed_password = bcrypt.hashpw("test123".encode("utf-8"), bcrypt.gensalt())
        user = User(email="test@example.com", password=hashed_password)
        db.session.add(user)

        event = Event(name="Test Event", date=datetime.utcnow(), price=100.0, stock=10)
        db.session.add(event)
        db.session.commit()

        user_id = user.id
        event_id = event.id

    # Maintenant, dans le contexte client (requête), on récupère les objets attachés à la session
    with client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True

        # Recharger les objets depuis la base pour qu'ils soient attachés à la session active
        user = User.query.get(user_id)
        event = Event.query.get(event_id)

        yield client, user, event
