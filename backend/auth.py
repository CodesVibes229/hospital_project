from flask import Blueprint, request, jsonify, make_response
import jwt
import datetime
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Blueprint('auth', __name__)
DATABASE = 'database.db'
SECRET_KEY = 'votre_cle_secrete'

# Connexion
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Token requis pour accéder à certaines routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-tokens')
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            conn = get_db_connection()
            current_user = conn.execute('SELECT * FROM users WHERE id = ?', (data['id'],)).fetchone()
            conn.close()
        except:
            return jsonify({'message': 'Token invalide'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Création d'un nouvel utilisateur (inscription)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')

    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                 (data['username'], hashed_password, data.get('role', 'user')))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Utilisateur enregistré avec succès'})

# Connexion (login) et génération de token
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Identifiants invalides', 401)

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (auth['username'],)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], auth['password']):
        return make_response('Identifiants invalides', 401)

    token = jwt.encode({'id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)}, SECRET_KEY)
    return jsonify({'token': token})

# Route protégée (accessible uniquement si authentifié)
@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Bonjour {current_user["username"]}, vous avez accès à cette route'})

# Gestion des rôles pour accès admin
@app.route('/admin', methods=['GET'])
@token_required
def admin_route(current_user):
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Accès refusé. Admin uniquement.'}), 403

    return jsonify({'message': 'Bienvenue admin !'})

# Initialisation de la base de données (pour tests)
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
