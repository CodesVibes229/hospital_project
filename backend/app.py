from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hospitals')
def hospital_list():
    conn = get_db_connection()
    hospitals = conn.execute('SELECT * FROM hospitals').fetchall()
    conn.close()
    return render_template('hospital_list.html', hospitals=hospitals)

@app.route('/add-hospital', methods=['GET', 'POST'])
def add_hospital():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        availability = request.form['availability']
        services = request.form['services']

        conn = get_db_connection()
        conn.execute('INSERT INTO hospitals (name, address, phone, availability, services) VALUES (?, ?, ?, ?, ?)',
                     (name, address, phone, availability, services))
        conn.commit()
        conn.close()
        return redirect(url_for('hospital_list'))

    return render_template('hospital_form.html')

@app.route('/delete-hospital/<int:id>')
def delete_hospital(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM hospitals WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('hospital_list'))

if __name__ == '__main__':
    app.run(debug=True)
