# 🏅 ProjetJO2024 – Application Web Flask

Application web développée en **Python (Flask)** pour la gestion de billets des **Jeux Olympiques 2024**, avec :

- Authentification sécurisée
- Paiement Stripe
- Génération de code-barres avec **JsBarcode (côté front)**
- Interface utilisateur et administrateur

---

## 🚀 Fonctionnalités

- ✅ Inscription / Connexion sécurisées avec **bcrypt**
- ✅ Système de panier pour utilisateurs anonymes et connectés
- ✅ Interface admin : gestion des offres, utilisateurs, paiements
- ✅ Intégration **Stripe** pour les paiements sécurisés
- ✅ Génération de **code-barres côté front** via **JsBarcode**
- ✅ Utilisation d’un fichier `.env` pour les clés sensibles
- ✅ Affichage dynamique des tickets après achat
- 🔒 Gestion sécurisée des sessions, inputs et mot de passe

---

## ⚙️ Technologies utilisées

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Bcrypt
- Stripe API
- JsBarcode (CDN)
- SQLite / MySQL
- Dotenv

---

## 📦 Installation locale

### 1. Cloner le projet

```bash
git clone https://github.com/ton-utilisateur/projet-jo2024.git
cd projet-jo2024
2. Créer un environnement virtuel
bash
Copier
Modifier
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
3. Installer les dépendances
bash
Copier
Modifier
pip install -r requirements.txt
4. Configurer les variables d’environnement
Créer un fichier .env à la racine du projet :

ini
Copier
Modifier
SECRET_KEY=une_clé_ultra_secrète
STRIPE_SECRET_KEY=sk_test_...
YOUR_DOMAIN=http://localhost:5000
🗃️ Base de données
Utilise SQLite par défaut (modifiable pour MySQL/PostgreSQL)

Exemple de table utilisateur (SQLite/MySQL) :

sql
Copier
Modifier
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password BLOB NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);
⚠️ Le champ password doit être en BLOB pour fonctionner avec bcrypt.

▶️ Lancer l’application
bash
Copier
Modifier
python app.py
Accès :
📍 http://localhost:5000

👮 Accès administrateur
Pour accéder à /admin, un utilisateur doit avoir :

sql
Copier
Modifier
is_admin = TRUE
💳 Paiement avec Stripe
Le backend utilise l’API Stripe pour créer des sessions de paiement.

Une fois le paiement validé, une transaction est enregistrée.

Un code-barres unique est généré côté front avec JsBarcode, basé sur un identifiant ou token sécurisé renvoyé par le backend.

📟 Génération du code-barres (via JsBarcode)
Dans la page de confirmation, un code-barres est généré automatiquement à partir des données renvoyées par le backend :

html
Copier
Modifier

🛠️ À améliorer / à venir
🧱 Structuration en modules (routes, models, services, etc.)

✅ Tests automatisés (unitaires et fonctionnels)

📦 Déploiement sur Render / Fly.io / o2switch / Railway

📧 Envoi d’e-mails avec code-barres en pièce jointe

📱 Design responsive / PWA

📄 Licence
Projet réalisé à des fins pédagogiques dans le cadre des Jeux Olympiques de Paris 2024.
Développé par [Ton Prénom NOM] — Tous droits réservés.

🔗 Liens utiles
Stripe API Docs

Flask Documentation

JsBarcode

Fly.io

o2Switch
