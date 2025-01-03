import logging
import os
import sys
import jwt
from functools import wraps
import secrets
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import sqlite3
import datetime
from backend.auth import app as auth_blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from backend.auth import SECRET_KEY

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
DATABASE = 'database.db'
secret_key = secrets.token_hex(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.register_blueprint(auth_blueprint, url_prefix='/auth')

logging.basicConfig(filename='logs/app.log', level=logging.DEBUG)

# Connexion
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    print(f"Connexion à la base de données : {DATABASE}")  # Pour vérifier le chemin de la base de données
    return conn


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

@app.route('/')
@app.route('/')
def index():
    token = request.cookies.get('token')  # Récupérer le token du cookie

    if not token:  # Pas de token = redirection vers login
        flash('Veuillez vous connecter.', 'danger')
        return redirect(url_for('auth.login'))

    try:
        # Décoder le token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded['id']  # Récupérer l'ID utilisateur du token
        session['user_id'] = user_id

        # Connexion à la base de données et récupération des hôpitaux
        conn = get_db_connection()
        hospitals = conn.execute('SELECT * FROM hospitals').fetchall()
        conn.close()

        # Affichage de la page index avec les hôpitaux
        return render_template('index.html', hospitals=hospitals, user_id=user_id)

    except jwt.ExpiredSignatureError:
        # Token expiré
        flash('Votre session a expiré. Veuillez vous reconnecter.', 'danger')
        return redirect(url_for('auth.login'))

    except jwt.InvalidTokenError:
        # Token invalide (falsifié ou corrompu)
        flash('Authentification invalide. Veuillez vous reconnecter.', 'danger')
        return redirect(url_for('auth.login'))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/create-user', methods=['GET'])
@token_required
def create_user_page(current_user):
    # Vérifie si l'utilisateur est un administrateur avant de lui permettre de créer un utilisateur
    if current_user['role'] != 'admin':
        flash('Accès interdit. Seul un administrateur peut créer un utilisateur.', 'error')
        return redirect(url_for('index'))

    return render_template('create_user.html')

@app.route('/create-user', methods=['POST'])
@token_required
def create_user(current_user):
    # Vérifie si l'utilisateur est un administrateur
    if current_user['role'] != 'admin':
        flash('Accès interdit. Seul un administrateur peut créer un utilisateur.', 'error')
        return redirect(url_for('index'))

    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username or not password:
        flash('Nom d\'utilisateur et mot de passe sont requis.', 'error')
        return redirect(url_for('auth.create_user_page'))

    # Hash du mot de passe
    hashed_password = generate_password_hash(password, method='sha256')

    try:
        conn = get_db_connection()
        # Vérifie si l'utilisateur existe déjà
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if existing_user:
            flash('Un utilisateur avec ce nom d\'utilisateur existe déjà.', 'error')
            return redirect(url_for('auth.create_user_page'))

        # Insertion du nouvel utilisateur dans la base de données
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     (username, hashed_password, role))
        conn.commit()
        conn.close()

        flash('Utilisateur créé avec succès.', 'success')
        return redirect(url_for('index'))

    except sqlite3.OperationalError as e:
        flash(f"Erreur de base de données: {str(e)}", 'error')
        return redirect(url_for('auth.create_user_page'))


# Liste des hôpitaux avec filtre par service
@app.route('/hospitals')
def hospital_list():
    service_filter = request.args.get('service_filter')
    conn = get_db_connection()
    if service_filter:
        hospitals = conn.execute('SELECT * FROM hospitals WHERE services LIKE ?', ('%' + service_filter + '%',)).fetchall()
    else:
        hospitals = conn.execute('SELECT * FROM hospitals').fetchall()
    conn.close()
    return render_template('hospital_list.html', hospitals=hospitals, service_filter=service_filter)

# Ajout d'hôpital avec latitude/longitude
@app.route('/add-hospital', methods=['GET', 'POST'])
def add_hospital():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        availability = request.form['availability']
        services = request.form['services']
        lat = request.form['lat']
        lng = request.form['lng']
        conn = get_db_connection()
        conn.execute('INSERT INTO hospitals (name, address, phone, availability, services, lat, lng) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (name, address, phone, availability, services, lat, lng))
        conn.commit()
        conn.close()
        return redirect(url_for('hospital_list'))

    return render_template('hospital_form.html')

# Suppression d'hôpital
@app.route('/delete-hospital/<int:id>')
def delete_hospital(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM hospitals WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('hospital_list'))

# Ajout d'avis pour un hôpital
@app.route('/add-review', methods=['POST'])
def add_review():
    hospital_id = request.form['hospital_id']
    rating = request.form['rating']
    comment = request.form['comment']

    conn = get_db_connection()
    conn.execute('INSERT INTO reviews (hospital_id, rating, comment) VALUES (?, ?, ?)',
                 (hospital_id, rating, comment))
    conn.commit()
    conn.close()

    return redirect(url_for('hospital_list'))


@app.route('/hospital/<int:id>')
def hospital_details(id):
    conn = get_db_connection()
    hospital = conn.execute('SELECT * FROM hospitals WHERE id = ?', (id,)).fetchone()
    conn.close()

    if hospital is None:
        return "Hôpital non trouvé", 404

    return render_template('hospital_details.html', hospital=hospital)


@app.route('/hospital/<int:hospital_id>/doctors')
def view_doctors(hospital_id):
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM doctors WHERE hospital_id = ?', (hospital_id,)).fetchall()
    conn.close()

    if not doctors:
        return "Aucun médecin trouvé pour cet hôpital", 404

    return render_template('doctors_list.html', doctors=doctors)


# API pour obtenir les hôpitaux en JSON (optionnel)
@app.route('/api/hospitals')
def api_hospitals():
    conn = get_db_connection()
    hospitals = conn.execute('SELECT * FROM hospitals').fetchall()
    conn.close()
    return jsonify([dict(hospital) for hospital in hospitals])

if __name__ == '__main__':
    app.run(debug=True)
