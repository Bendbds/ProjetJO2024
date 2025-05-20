import os
import uuid
import bcrypt
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# --- Extensions instanciées une seule fois ---
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# --- MODELS ---

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=100)

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    offer_name = db.Column(db.String(100))
    price = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref('cart_items', lazy=True))

class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    barcode_value = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='tickets')
    event = db.relationship('Event', backref='tickets')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- FONCTION USINE ---
def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'devkey')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ⚠️ Appliquer config de test si elle est passée
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # --- Auxiliaire pour panier ---
    def get_cart_items():
        if current_user.is_authenticated:
            return CartItem.query.filter_by(user_id=current_user.id).all()
        else:
            return []

    # --- ROUTES ---

    @app.route('/')
    def index():
        events = Event.query.all()
        return render_template('index.html', events=events)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            if User.query.filter_by(email=email).first():
                flash("Email déjà utilisé.")
                return redirect(url_for('register'))
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = User(email=email, password=hashed)
            db.session.add(user)
            db.session.commit()
            flash("Inscription réussie")
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
                login_user(user)
                flash("Connecté")
                return redirect(url_for('index'))
            flash("Email ou mot de passe incorrect")
            return redirect(url_for('login'))
        return render_template('connexion.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("Déconnecté")
        return redirect(url_for('index'))

    @app.route('/panier')
    @login_required
    def panier():
        items = get_cart_items()
        total = sum(i.price for i in items)
        return render_template('panier.html', items=items, total=total)

    @app.route('/add_to_cart', methods=['POST'])
    @login_required
    def add_to_cart():
        data = request.get_json()
        event_id = data.get('event_id')
        event = Event.query.get(event_id)
        if not event or event.stock <= 0:
            return jsonify({"message": "Événement indisponible"}), 400
        cart_item = CartItem(offer_name=event.name, price=event.price, user_id=current_user.id, event_id=event_id)
        db.session.add(cart_item)
        event.stock -= 1
        db.session.commit()
        return jsonify({"message": "Ajouté au panier"}), 200

    @app.route('/success')
    @login_required
    def success():
        items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not items:
            flash("Panier vide")
            return redirect(url_for('panier'))
        tickets = []
        for item in items:
            ticket = Ticket(user_id=current_user.id, event_id=item.event_id, barcode_value=str(uuid.uuid4()))
            tickets.append(ticket)
        db.session.add_all(tickets)
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash("Paiement réussi, billets créés")
        return redirect(url_for('mes_billets'))

    @app.route('/mes_billets')
    @login_required
    def mes_billets():
        tickets = Ticket.query.filter_by(user_id=current_user.id).all()
        return render_template('mes_billets.html', tickets=tickets)

    # --- Route test simple billets ---
    @app.route('/test_billet', methods=['GET', 'POST'])
    def test_billet():
        if request.method == 'POST':
            data = request.get_json()
            user_email = data.get('email')
            event_name = data.get('event')
            user = User.query.filter_by(email=user_email).first()
            event = Event.query.filter_by(name=event_name).first()
            if not user or not event:
                return jsonify({"message": "Utilisateur ou événement non trouvé"}), 404
            ticket = Ticket(user_id=user.id, event_id=event.id, barcode_value=str(uuid.uuid4()))
            db.session.add(ticket)
            db.session.commit()
            return jsonify({"message": "Ticket créé", "ticket_id": ticket.id}), 201
        else:
            tickets = Ticket.query.all()
            return jsonify([{"id": t.id, "user": t.user.email, "event": t.event.name, "barcode": t.barcode_value} for t in tickets])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)