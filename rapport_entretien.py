from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import subprocess
import traceback
import os
import sys
import time



app = Flask(__name__)
CORS(app)

DATABASE = "rh_chatbot.db"

# --- Routes pour servir fichiers statiques ---
@app.route('/static/photos_candidats/<path:filename>')
def serve_photo(filename):
    return send_from_directory('static/photos_candidats', filename)

@app.route('/static/rapports_pdf/<path:filename>')
def serve_pdf(filename):
    return send_from_directory('static/rapports_pdf', filename)

# --- Création des tables SQLite si besoin ---
def create_table_if_not_exists():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS rapport_entretien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_candidat TEXT,
            nom TEXT,
            prenom TEXT,
            photo TEXT,
            etat TEXT,
            rapport_pdf TEXT,
            score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            mot_de_passe TEXT NOT NULL,
            photo TEXT,
            date_entretien DATETIME
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT,
            email TEXT,
            societe TEXT,
            pays TEXT,
            sujet TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

# --- Connexion ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    nom = data.get('nom', '').strip()
    prenom = data.get('prenom', '').strip()
    mot_de_passe = data.get('mot_de_passe', '').strip()

    if not nom or not prenom or not mot_de_passe:
        return jsonify({"success": False, "message": "Tous les champs sont obligatoires"}), 400

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE nom=? AND prenom=? AND mot_de_passe=?", (nom, prenom, mot_de_passe))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "message": "Connexion réussie"})
    else:
        return jsonify({"success": False, "message": "Nom, prénom ou mot de passe incorrect"})

# --- Lancer un test ---
@app.route('/api/demarrer_test', methods=['POST'])
def demarrer_test():
    data = request.json
    id_candidat = data.get('id_candidat')
    nom = data.get('nom')
    prenom = data.get('prenom')

    if not id_candidat or not nom or not prenom:
        return jsonify({"error": "id_candidat, nom et prenom sont requis"}), 400

    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO rapport_entretien (id_candidat, nom, prenom, etat)
            VALUES (?, ?, ?, ?)
        """, (id_candidat, nom, prenom, "En cours"))
        conn.commit()
        conn.close()

        # Lancement du script deepface en tâche de fond
        subprocess.Popen(['python', 'analyse_entretien.py', id_candidat, nom, prenom])

        return jsonify({"message": "Test lancé"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Terminer un test (mettre à jour état) ---
@app.route('/api/fin_test', methods=['POST'])
def fin_test():
    try:
        data = request.json
        id_candidat = data.get('id_candidat')
        etat = data.get('etat', 'Terminé')

        if not id_candidat:
            return jsonify({"error": "id_candidat est requis"}), 400

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            SELECT id FROM rapport_entretien WHERE id_candidat = ? ORDER BY timestamp DESC LIMIT 1
        """, (id_candidat,))
        row = c.fetchone()

        if not row:
            return jsonify({"error": "Aucun rapport trouvé pour ce candidat"}), 404

        c.execute("""
            UPDATE rapport_entretien SET etat = ? WHERE id = ?
        """, (etat, row[0]))
        conn.commit()
        conn.close()

        return jsonify({"message": "État mis à jour avec succès"}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --- Liste des rapports ---
@app.route('/api/rapports', methods=['GET'])
def api_rapports():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            SELECT id, id_candidat, nom, prenom, photo, etat, rapport_pdf, score, timestamp
            FROM rapport_entretien ORDER BY timestamp DESC
        """)
        rows = c.fetchall()
        conn.close()

        rapports = []
        for r in rows:
            rapports.append({
                "id": r[0],
                "id_candidat": r[1],
                "nom": r[2],
                "prenom": r[3],
                "photo": r[4] if r[4] else "",
                "etat": r[5],
                "rapport_pdf": r[6] if r[6] else "",
                "score": r[7] if r[7] is not None else 0.0,
                "timestamp": r[8]
            })

        return jsonify(rapports)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# --- Liste des messages de contact ---
@app.route('/api/contact_messages', methods=['GET'])
def api_contact_messages():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM contact_messages ORDER BY timestamp DESC")
        rows = c.fetchall()
        conn.close()

        return jsonify([{
            "id": r[0], "nom": r[1], "prenom": r[2], "email": r[3],
            "societe": r[4], "pays": r[5], "sujet": r[6],
            "message": r[7], "timestamp": r[8]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Enregistrement message contact ---
@app.route('/api/contact', methods=['POST'])
def api_contact_post():
    try:
        data = request.json
        champs = ['nom', 'prenom', 'email', 'societe', 'pays', 'sujet', 'message']
        if not all(data.get(champ, '').strip() for champ in champs):
            return jsonify({"error": "Tous les champs sont obligatoires"}), 400

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO contact_messages (nom, prenom, email, societe, pays, sujet, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tuple(data[ch] for ch in champs))
        conn.commit()
        conn.close()

        return jsonify({"message": "Message enregistré avec succès"}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



def update_rapport_db(id_candidat, chemin_photo, pdf_path, score):
    conn = sqlite3.connect("rh_chatbot.db")
    c = conn.cursor()

    c.execute("SELECT id FROM rapport_entretien WHERE id_candidat = ? AND etat = 'En cours'", (id_candidat,))
    row = c.fetchone()

    if row:
        c.execute("""
            UPDATE rapport_entretien
            SET photo = ?, rapport_pdf = ?, score = ?, etat = 'Terminé', timestamp = CURRENT_TIMESTAMP
            WHERE id_candidat = ? AND etat = 'En cours'
        """, (chemin_photo, pdf_path, score, id_candidat))
        print("[RH] ✅ Rapport mis à jour.")
    else:
        # insère directement un nouveau rapport
        c.execute("""
            INSERT INTO rapport_entretien (id_candidat, photo, rapport_pdf, score, etat)
            VALUES (?, ?, ?, ?, 'Terminé')
        """, (id_candidat, chemin_photo, pdf_path, score))
        print("[RH] 🆕 Rapport inséré car aucun 'En cours' trouvé.")

    conn.commit()
    conn.close()

# --- Exécution ---
if __name__ == '__main__':
    create_table_if_not_exists()
    app.run(host='0.0.0.0', port=5000, debug=True)