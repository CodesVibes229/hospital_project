
# Gestion des Hôpitaux, Centres de Santé et Cliniques

Une application web développée avec Flask pour centraliser les informations des hôpitaux, centres de santé, cliniques et dispensaires d’un pays.

## Fonctionnalités
- Ajouter un hôpital avec ses informations (nom, adresse, téléphone, disponibilité, services).
- Afficher la liste des hôpitaux avec leurs détails.
- API REST pour gérer les données.

---

## Structure du Projet
```
project/
│
├── backend/
│   ├── app.py                 # Serveur Flask et routes principales
│   ├── database.db            # Fichier SQLite pour stocker les données
│   ├── init_db.py             # Script pour initialiser la base de données
│   └── models.py              # (Facultatif) Gestion des modèles de données
│
├── frontend/
│   ├── templates/             # Pages HTML
│   │   ├── index.html         # Page d'accueil
│   │   ├── hospital_form.html # Formulaire d'ajout d'hôpital
│   │   └── hospital_list.html # Liste des hôpitaux
│   │
│   ├── static/                # Fichiers statiques
│       ├── css/
│       │   └── styles.css     # Feuille de styles
│       ├── js/
│       │   └── scripts.js     # Scripts JavaScript
│       └── images/            # Images (si nécessaire)
│
└── README.md                  # Documentation du projet
```

---

## Installation

### Prérequis
- Python 3.8 ou une version ultérieure
- pip (le gestionnaire de paquets Python)

### Étapes
1. Clonez ce dépôt :
   ```bash
   git clone <https://github.com/CodesVibes229/hospital_project.git>
   cd project
   ```

2. Accédez au dossier `backend` :
   ```bash
   cd backend
   ```

3. Installez les dépendances Python :
   ```bash
   pip install flask
   ```

4. Initialisez la base de données :
   ```bash
   python init_db.py
   ```

5. Lancez le serveur Flask :
   ```bash
   python app.py
   ```

6. Ouvrez votre navigateur et accédez à `http://127.0.0.1:5000`.

---

## API Endpoints

### **GET /api/hospitals**
Récupère la liste de tous les hôpitaux.

#### Exemple de réponse
```json
[
    {
        "id": 1,
        "name": "Hôpital Général",
        "address": "123 Rue Principale",
        "phone": "0123456789",
        "availability": "Disponible",
        "services": "Urgence, Consultation Générale"
    }
]
```

### **POST /api/hospitals**
Ajoute un nouvel hôpital.

#### Corps de la requête
```json
{
    "name": "Clinique Saint-Pierre",
    "address": "456 Avenue de la Santé",
    "phone": "9876543210",
    "availability": "Non disponible",
    "services": "Pédiatrie, Radiologie"
}
```

#### Exemple de réponse
```json
{
    "message": "Hôpital ajouté avec succès!"
}
```

---

## Auteur
Développé par [Harold].