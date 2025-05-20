from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import stripe
import uuid
import bcrypt
import pymysql
pymysql.install_as_MySQLdb()

from models import db, User, Event, CartItem, Ticket
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

stripe.api_key = app.config['STRIPE_SECRET_KEY']
YOUR_DOMAIN = app.config['YOUR_DOMAIN']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    if request.endpoint == 'add_to_cart' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"message": "Vous devez être connecté pour ajouter au panier."}), 401
    return redirect(url_for('login'))

def get_cart_items():
    if current_user.is_authenticated:
        return CartItem.query.filter_by(user_id=current_user.id).all()
    else:
        temp_id = session.get("temp_user_id")
        if not temp_id:
            temp_id = str(uuid.uuid4())
            session["temp_user_id"] = temp_id
        return CartItem.query.filter_by(temp_user_id=temp_id).all()

@app.route('/')
def index():
    events = Event.query.all()
    for event in events:
        if isinstance(event.date, datetime):
            event.formatted_date = event.date.strftime("%d %B %Y")
        else:
            event.formatted_date = event.date
    return render_template('index.html', events=events)

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
        confirm_password = request.form['confirm_password']
        user = User.query.filter_by(email=email).first()

        # Vérification si les mots de passe saisis ne correspondent pas
        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "error")
            return redirect(url_for('login'))

        # Vérification que l'utilisateur existe et que son mot de passe est valide
        if not user or not isinstance(user.password, (bytes, bytearray)):
            flash("Email ou mot de passe incorrect.", "error")
            return redirect(url_for('login'))

        try:
            # Vérification du mot de passe sans encoder à nouveau le hash
            if not bcrypt.checkpw(password.encode('utf-8'), user.password):
                flash("Email ou mot de passe incorrect.", "error")
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Erreur avec bcrypt: {e}")  # Log pour debug
            flash("Une erreur est survenue lors de la vérification du mot de passe.", "error")
            return redirect(url_for('login'))

        # Connexion réussie
        login_user(user)
        flash("Connexion réussie.", "success")
        return redirect(url_for('index'))

    return render_template('connexion.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.")
    return redirect(url_for('index'))

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        # Récupérer les données JSON envoyées par le front-end
        data = request.get_json()
        title = data.get("title")
        price = float(data.get("price"))
        event_id = data.get("event_id")
        
        # Trouver l'événement pour vérifier le stock
        event = Event.query.get(event_id)
        
        if not event:
            return jsonify({"message": "Événement introuvable."}), 404
        
        if event.stock <= 0:
            return jsonify({"message": "Désolé, cet événement est complet."}), 400
        
        # Créer un nouvel article de panier pour l'utilisateur authentifié
        cart_item = CartItem(
            offer_name=title,
            price=price,
            event_id=event_id,
            user_id=current_user.id  # On associe cet article à l'utilisateur connecté
        )
        
        # Ajouter l'article au panier (dans la base de données)
        db.session.add(cart_item)
        event.stock -= 1  # Décrémenter le stock de l'événement immédiatement
        db.session.commit()
        
        # Retourner un message de succès
        return jsonify({"message": "Ajouté au panier !"}), 200
    
    except Exception as e:
        db.session.rollback()  # En cas d'erreur, annuler la transaction
        return jsonify({"message": f"Erreur de communication avec le serveur: {str(e)}"}), 500

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    try:
        # Trouver l'article dans le panier de l'utilisateur
        cart_item = CartItem.query.get(item_id)
        
        if cart_item is None:
            return jsonify({"message": "Article introuvable dans le panier."}), 404
        
        # Vérifier si l'article appartient à l'utilisateur connecté
        if cart_item.user_id != current_user.id:
            return jsonify({"message": "Vous ne pouvez pas supprimer cet article."}), 403
        
        # Récupérer l'événement associé à l'article du panier
        event = Event.query.get(cart_item.event_id)
        if event:
            # Rétablir le stock de l'événement (augmenter de 1)
            event.stock += 1
        
        # Supprimer l'article du panier
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({"message": "Article supprimé du panier avec succès !"}), 200
    
    except Exception as e:
        db.session.rollback()  # Annuler la transaction en cas d'erreur
        return jsonify({"message": f"Erreur de communication avec le serveur: {str(e)}"}), 500

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
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for item in cart_items:
            event = Event.query.get(item.event_id)
            if event:
                event.stock += 1
        CartItem.query.filter_by(user_id=current_user.id).delete()
    else:
        temp_id = session.get('temp_user_id')
        if temp_id:
            cart_items = CartItem.query.filter_by(temp_user_id=temp_id).all()
            for item in cart_items:
                event = Event.query.get(item.event_id)
                if event:
                    event.stock += 1
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

    try:
        session_stripe = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': item.offer_name},
                    'unit_amount': int(item.price * 100),
                },
                'quantity': 1,
            } for item in items],
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
    try:
        items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not items:
            flash("Votre panier est vide.", "warning")
            return redirect(url_for('panier'))

        tickets = []

        for item in items:
            if item.event:
                if item.event.stock > 0:
                    item.event.stock -= 1
                else:
                    flash(f"Stock insuffisant pour {item.offer_name}.", "danger")
                    return redirect(url_for('panier'))

                # Création du ticket avec valeur unique pour code-barres
                ticket = Ticket(
                    user_id=current_user.id,
                    event_id=item.event_id,
                    qr_code_filename=None,
                    barcode_value=str(uuid.uuid4()),  # <-- Valeur unique pour le code-barres
                    created_at=datetime.utcnow()
                )
                tickets.append(ticket)

        db.session.add_all(tickets)
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        flash("Paiement réussi ! Vos billets sont disponibles.", "success")
        return redirect(url_for('mes_billets'))

    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur est survenue : {e}", "danger")
        return redirect(url_for('panier'))

@app.route('/mes_billets')
@login_required
def mes_billets():
    try:
        tickets = Ticket.query.filter_by(user_id=current_user.id).all()
        for ticket in tickets:
            ticket.qr_code_content = ticket.barcode_value  # Ajout du contenu du code-barres
        return render_template('mes_billets.html', tickets=tickets)
    except Exception as e:
        flash(f"Erreur lors du chargement de vos billets : {e}", "danger")
        return redirect(url_for('index'))
        
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

    try:
        price = float(price)
        event_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        event_end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    except ValueError:
        flash("Erreur de format pour la date ou le prix.")
        return redirect(url_for('admin_dashboard'))

    new_event = Event(name=name, date=event_start_date, price=price, end_date=event_end_date)
    db.session.add(new_event)
    db.session.commit()
    flash("Événement ajouté avec succès!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get(event_id)
    if request.method == 'POST':
        event.name = request.form['name']
        event.date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = request.form.get('end_date')
        if end_date:
            event.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        event.price = request.form['price']
        db.session.commit()
        flash('Événement mis à jour avec succès!', 'success')
        return redirect(url_for('index'))
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
