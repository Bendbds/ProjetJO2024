import os
import uuid
import stripe
import bcrypt
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user, login_required,
    current_user, UserMixin
)
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser Flask
app = Flask(__name__)

# Configurations via .env
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Stripe config
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
YOUR_DOMAIN = 'http://localhost:5000'

# ---------------------
# MODELS
# ---------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(60), nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    offer_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    temp_user_id = db.Column(db.String(100), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------
# UTILITAIRES
# ---------------------

def get_cart_items():
    if current_user.is_authenticated:
        return CartItem.query.filter_by(user_id=current_user.id).all()
    else:
        if 'temp_user_id' not in session:
            session['temp_user_id'] = str(uuid.uuid4())
            session.modified = True
        return CartItem.query.filter_by(temp_user_id=session['temp_user_id']).all()

# ---------------------
# ROUTES
# ---------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.")
            return redirect(url_for('register'))

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Inscription réussie.")
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
            flash("Connexion réussie.")
            return redirect(url_for('index'))
        else:
            flash("Email ou mot de passe invalide.")
            return redirect(url_for('login'))

    return render_template('connexion.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.")
    return redirect(url_for('index'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        offer_name = data['title']
        price = float(data['price'])

        if current_user.is_authenticated:
            user_id = current_user.id
            temp_user_id = None
        else:
            user_id = None
            if 'temp_user_id' not in session:
                session['temp_user_id'] = str(uuid.uuid4())
            temp_user_id = session['temp_user_id']

        item = CartItem(
            offer_name=offer_name,
            price=price,
            user_id=user_id,
            temp_user_id=temp_user_id
        )
        db.session.add(item)
        db.session.commit()

        return '', 200
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({'error': 'Vous devez être connecté pour ajouter un article panier'}), 500

@app.route('/cart')
def cart():
    items = get_cart_items()
    cart_items = [{'offer_name': item.offer_name, 'price': item.price} for item in items]
    return jsonify(cart_items)

@app.route('/panier')
def panier():
    items = get_cart_items()
    total = sum(item.price for item in items)
    return render_template('panier.html', items=items, total=total, is_logged_in=current_user.is_authenticated)

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if current_user.is_authenticated:
        CartItem.query.filter_by(user_id=current_user.id).delete()
    else:
        temp_id = session.get('temp_user_id')
        if temp_id:
            CartItem.query.filter_by(temp_user_id=temp_id).delete()
    db.session.commit()
    return '', 204

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    items = get_cart_items()
    if not items:
        flash("Votre panier est vide.")
        return redirect(url_for('panier'))

    line_items = [
        {
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': item.offer_name},
                'unit_amount': int(item.price * 100),
            },
            'quantity': 1,
        } for item in items
    ]

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/panier',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Erreur Stripe: {e}")
        return redirect(url_for('panier'))

@app.route('/success')
@login_required
def success():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return "Paiement réussi. Merci !"

# ---------------------
# MAIN
# ---------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
