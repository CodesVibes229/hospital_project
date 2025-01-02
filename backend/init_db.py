import sqlite3
from werkzeug.security import generate_password_hash
DATABASE = 'database.db'


def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Création ou modification de la table des hôpitaux
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            availability TEXT NOT NULL,
            services TEXT NOT NULL
        )
    ''')

    # Ajout des colonnes de géolocalisation si elles n'existent pas encore
    try:
        cursor.execute('ALTER TABLE hospitals ADD COLUMN lat REAL')
        cursor.execute('ALTER TABLE hospitals ADD COLUMN lng REAL')
        print("Colonnes 'lat' et 'lng' ajoutées avec succès.")
    except sqlite3.OperationalError:
        print("Colonnes 'lat' et 'lng' déjà existantes.")

    # Création de la table des avis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_id INTEGER,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospital_id) REFERENCES hospitals (id) ON DELETE CASCADE
        )
    ''')

    # Création de la table des spécialités
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS specialties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Création de la table des médecins
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty_id INTEGER,
            hospital_id INTEGER,
            phone TEXT,
            email TEXT,
            FOREIGN KEY (specialty_id) REFERENCES specialties (id) ON DELETE SET NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals (id) ON DELETE CASCADE
        )
    ''')

    # --- modif_log : Création de la table users ---
    # Création de la table des utilisateurs (si elle n'existe pas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # Ajout d'un utilisateur admin par défaut
    default_admin = ('admin', generate_password_hash('admin123', method='sha256'), 'admin')
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', default_admin)

    # Insertion de quelques spécialités par défaut (si la table est vide)
    cursor.execute(
        "INSERT OR IGNORE INTO specialties (id, name) VALUES (1, 'Cardiologie'), (2, 'Pédiatrie'), (3, 'Chirurgie')"
    )

    conn.commit()
    conn.close()
    print("Base de données et tables initialisées avec succès!")


if __name__ == '__main__':
    create_database()
