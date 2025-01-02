from flask import Blueprint, request, jsonify, make_response, render_template, redirect, url_for, flash, session
import jwt
import datetime
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Blueprint('auth', __name__)
DATABASE = 'database.db'
SECRET_KEY = 'votre_cle_secrete'


# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Token requis pour accéder à certaines routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            flash('Vous devez vous connecter.', 'error')
            return redirect(url_for('auth.login'))  # Redirection vers la page de connexion
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            conn = get_db_connection()
            current_user = conn.execute('SELECT * FROM users WHERE id = ?', (data['id'],)).fetchone()
            conn.close()
        except:
            flash('Votre session a expiré.', 'error')
            return redirect(url_for('auth.login'))

        return f(current_user, *args, **kwargs)

    return decorated


# Route pour afficher la page de connexion
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


# Route pour gérer la connexion et générer un token
@app.route('/login', methods=['POST'])
def login():
    auth = request.form  # Récupérer les données du formulaire

    if not auth or not auth.get('username') or not auth.get('password'):
        flash('Identifiants invalides', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (auth['username'],)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], auth['password']):
        flash('Identifiants invalides', 'error')
        return redirect(url_for('auth.login'))

    token = jwt.encode({'id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)},
                       SECRET_KEY)

    response = make_response(redirect(url_for('index')))
    response.set_cookie('token', token)

    flash('Connexion réussie!', 'success')
    return response


# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('auth.login'))


# Route protégée (accessible uniquement après connexion)
@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Bonjour {current_user["username"]}, vous avez accès à cette route'})


# Route admin protégée
@app.route('/admin', methods=['GET'])
@token_required
def admin_route(current_user):
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Accès refusé. Admin uniquement.'}), 403

    return jsonify({'message': 'Bienvenue admin !'})


# Initialisation de la base de données (test uniquement)
@app.route('/init-db', methods=['GET'])
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                )''')
    conn.commit()
    conn.close()
    return jsonify({'message': 'Base de données initialisée'})
