import logging
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import sqlite3
from auth import app as auth_blueprint

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
DATABASE = 'database.db'
app.secret_key = os.urandom(24)
app.register_blueprint(auth_blueprint, url_prefix='/auth')

logging.basicConfig(filename='logs/app.log', level=logging.DEBUG)

# Connexion
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        flash('Veuillez vous connecter.', 'danger')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    hospitals = conn.execute('SELECT * FROM hospitals').fetchall()
    conn.close()
    return render_template('index.html', hospitals=hospitals)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


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
