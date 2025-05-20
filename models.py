from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    tickets = db.relationship('Ticket', backref='user', lazy=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=100)

    cart_items = db.relationship('CartItem', backref='event', lazy=True)
    tickets = db.relationship('Ticket', backref='event', lazy=True)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    offer_name = db.Column(db.String(100))
    price = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    temp_user_id = db.Column(db.String(36), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    qr_code_filename = db.Column(db.String(100))
    barcode_value = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
