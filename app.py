import os
import uuid
import stripe
import bcrypt
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import datetime
from flask_babel import Babel, format_datetime

# Charger les variables d'environnement
load_dotenv()

# Créer l'application Flask
app = Flask(__name__)

# Configuration de l'application
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration de Flask-Babel pour la gestion de la langue
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'

# Enregistrer les filtres pour que format_datetime fonctionne
app.jinja_env.filters['format_datetime'] = format_datetime

# ---------------------
# EXTENSIONS
# ---------------------

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # <-- ici !
login_manager = LoginManager(app)
login_manager.login_view = 'login'
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
YOUR_DOMAIN = 'http://localhost:5000'

# ---------------------
# MODELS
# ---------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    offer_name = db.Column(db.String(100))
    price = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    temp_user_id = db.Column(db.String(36))  # ID pour utilisateur temporaire
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))  # Relation avec Event
    event = db.relationship('Event', backref=db.backref('cart_items', lazy=True))  # Optionnel pour récupérer l'événement associé

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date de début
    end_date = db.Column(db.Date, nullable=True)  # Date de fin (optionnelle)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=100)  # Nombre max de places

# ---------------------
# FLASK-LOGIN
# ---------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------
# UTILITAIRES
# ---------------------

def get_cart_items():
    user_id = current_user.id if current_user.is_authenticated else session.get('temp_user_id')
    return CartItem.query.filter_by(user_id=user_id).all()

# ---------------------
# ROUTES : AUTHENTIFICATION
# ---------------------

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

# ---------------------
# ROUTES : ACCUEIL
# ---------------------

@app.route('/')
def index():
    events = Event.query.all()
    # Formater la date en français pour chaque événement
    for event in events:
        # Vérifier si la date est un objet Date
        if isinstance(event.date, datetime):
            event.formatted_date = event.date.strftime("%d %B %Y")  # Format en français
        else:
            event.formatted_date = event.date  # Si la date n'est pas un objet Date valide

    return render_template('index.html', events=events)

# ---------------------
# ROUTES : PANIER
# ---------------------

@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json()
    title = data["title"]
    price = float(data["price"])
    event_id = data["event_id"]

    # Log pour vérifier si les données arrivent
    print(f"Ajout au panier: {title}, {price}, {event_id}")

    event = Event.query.get(event_id)
    if event and event.stock > 0:
        if current_user.is_authenticated:
            cart_item = CartItem(event_id=event_id, user_id=current_user.id, offer_name=title, price=price)
        else:
            if 'temp_user_id' not in session:
                session['temp_user_id'] = str(uuid.uuid4())
            cart_item = CartItem(event_id=event_id, temp_user_id=session['temp_user_id'], offer_name=title, price=price)

        db.session.add(cart_item)
        event.stock -= 1
        db.session.commit()

        return jsonify({"message": "Ajouté au panier!"})
    else:
        return jsonify({"message": "Stock épuisé ou événement introuvable."}), 400

@app.route('/cart')
def cart():
    items = get_cart_items()
    return jsonify([{'offer_name': item.offer_name, 'price': item.price} for item in items])

@app.route('/panier')
def panier():
    items = get_cart_items()
    total = sum(item.price for item in items)
    return render_template('panier.html', items=items, total=total, is_logged_in=current_user.is_authenticated)

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if current_user.is_authenticated:
        # Récupérer les items du panier avant suppression
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        
        # Augmenter le stock des événements supprimés du panier
        for item in cart_items:
            event = Event.query.get(item.event_id)
            if event:
                event.stock += 1  # Ajouter une place au stock de l'événement supprimé
        CartItem.query.filter_by(user_id=current_user.id).delete()  # Supprimer tous les items du panier
    else:
        temp_id = session.get('temp_user_id')
        if temp_id:
            # Récupérer les items du panier pour l'utilisateur temporaire
            cart_items = CartItem.query.filter_by(temp_user_id=temp_id).all()
            
            # Augmenter le stock des événements supprimés du panier
            for item in cart_items:
                event = Event.query.get(item.event_id)
                if event:
                    event.stock += 1  # Ajouter une place au stock de l'événement supprimé
            CartItem.query.filter_by(temp_user_id=temp_id).delete()  # Supprimer les items du panier temporaire
    
    db.session.commit()
    return '', 204

# ---------------------
# ROUTES : PAIEMENT
# ---------------------

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    items = get_cart_items()
    if not items:
        flash("Votre panier est vide.")
        return redirect(url_for('panier'))

    try:
        session_stripe = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {'name': item.offer_name},
                        'unit_amount': int(item.price * 100),
                    },
                    'quantity': 1,
                } for item in items
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/panier',
        )
        return redirect(session_stripe.url, code=303)
    except Exception as e:
        flash(f"Erreur Stripe: {e}")
        return redirect(url_for('panier'))

@app.route('/success')
@login_required
def success():
    items = CartItem.query.filter_by(user_id=current_user.id).all()

    for item in items:
        if item.event:
            if item.event.stock > 0:
                item.event.stock -= 1
            else:
                flash(f"Stock insuffisant pour {item.offer_name}.")
                return redirect(url_for('panier'))

    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Paiement réussi. Merci !")
    return redirect(url_for('index'))

# ---------------------
# ROUTES : ADMINISTRATION
# ---------------------

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    events = Event.query.all()
    return render_template('admin.html', events=events)

@app.route('/admin/add_event', methods=['POST'])
@login_required
def add_event():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    name = request.form['name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    price = request.form['price']
    
    # Validation
    try:
        price = float(price)
    except ValueError:
        flash("Le prix doit être un nombre valide.")
        return redirect(url_for('admin_dashboard'))
    
    try:
        event_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        event_end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    except ValueError:
        flash("Les dates doivent être au format YYYY-MM-DD.")
        return redirect(url_for('admin_dashboard'))
    
    new_event = Event(name=name, date=event_start_date, price=price, end_date=event_end_date)
    db.session.add(new_event)
    db.session.commit()

    flash("Événement ajouté avec succès!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get(event_id)  # Récupère l'événement par son ID
    if request.method == 'POST':
        # Mise à jour de l'événement avec les nouvelles dates
        event.name = request.form['name']
        event.date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = request.form.get('end_date')  # La date de fin est optionnelle
        if end_date:
            event.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        event.price = request.form['price']
        db.session.commit()  # Sauvegarde dans la base de données
        flash('Événement mis à jour avec succès!', 'success')
        return redirect(url_for('index'))  # Redirige vers la page d'accueil ou la liste des événements
    return render_template('edit_event.html', event=event)

@app.route('/admin/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()

    flash("Événement supprimé avec succès!", "success")
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
