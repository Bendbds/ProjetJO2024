# ProjetJO2024
# Projet JO 2024 - Application Flask

Application web développée en Python avec Flask, permettant la gestion d'utilisateurs, une interface d'administration, et un système de paiement via Stripe.

## 🚀 Fonctionnalités

- Inscription et connexion sécurisées avec `bcrypt`
- Interface utilisateur et interface admin
- Intégration Stripe pour paiements
- Utilisation d'un fichier `.env` pour gérer les clés sensibles

---

## ⚙️ Technologies utilisées

- Python 3.x
- Flask
- Flask SQLAlchemy
- Bcrypt (pour hachage sécurisé des mots de passe)
- Stripe API
- Dotenv (.env)

---

## 📦 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/ton-utilisateur/projet-jo2024.git
cd projet-jo2024
2. Créer un environnement virtuel
bash
Copier
Modifier
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
3. Installer les dépendances
bash
Copier
Modifier
pip install -r requirements.txt
4. Configurer les variables d'environnement
Créer un fichier .env à la racine du projet avec le contenu suivant :

ini
Copier
Modifier
SECRET_KEY=une_clé_ultra_secrète
STRIPE_SECRET_KEY=sk_test_...
YOUR_DOMAIN=http://localhost:5000
🗃️ Base de données
Le projet utilise SQLite (ou autre selon votre config).

✅ Important :
Le champ password de la table User doit être de type BLOB pour fonctionner avec bcrypt.

Exemple avec HeidiSQL :

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
▶️ Lancer l'application
bash
Copier
Modifier
python app.py
Puis accéder à l'application via :

arduino
Copier
Modifier
http://localhost:5000
👮 Admin
Pour accéder à la partie admin, un utilisateur doit avoir is_admin = True dans la base.

💳 Paiement avec Stripe
Stripe est intégré à l'application.

Le backend gère la création de sessions de paiement via l'API.

YOUR_DOMAIN dans .env doit correspondre à l'URL de base utilisée (ex. : localhost ou domaine en production).

🛠️ À améliorer plus tard
Organisation du projet en modules (routes, models, config)

Ajout de tests automatisés

Déploiement sur Render, Heroku ou autre

📄 Licence
Projet développé à titre pédagogique dans le cadre des JO 2024.
