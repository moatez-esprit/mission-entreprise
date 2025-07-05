import cv2
from deepface import DeepFace
import time
import sqlite3
import os
from collections import defaultdict
from fpdf import FPDF

# --- Config ---
REFERENCE_IMAGE_PATH = "C:/Users/HP/Downloads/facial-analysis-service/test_image22.jpg"
PHOTO_SAVE_FOLDER = "static/photos_candidats"
PDF_FOLDER = "static/rapports_pdf"
DATABASE = "rh_chatbot.db"

regard_directions = {'haut': 0, 'bas': 0, 'gauche': 0, 'droite': 0}

emotion_colors = {
    'angry': (0, 0, 255), 'disgust': (0, 128, 0), 'fear': (128, 0, 128),
    'happy': (0, 255, 255), 'sad': (255, 0, 0), 'surprise': (0, 165, 255),
    'neutral': (255, 255, 255), 'stressé': (0, 0, 128)
}

def detecter_regard_direction(frame):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        region = result[0]['region'] if isinstance(result, list) else result['region']

        x, y, w, h = region['x'], region['y'], region['w'], region['h']
        cx = x + w / 2
        cy = y + h / 2

        largeur = frame.shape[1]
        hauteur = frame.shape[0]

        if cx < largeur * 0.3:
            return "gauche"
        elif cx > largeur * 0.7:
            return "droite"
        elif cy < hauteur * 0.3:
            return "haut"
        elif cy > hauteur * 0.7:
            return "bas"
        else:
            return "centre"
    except Exception as e:
        print(f"[RH] Erreur détection regard : {e}")
        return "indéterminé"

def afficher_emotion(frame, emotion, score):
    color = emotion_colors.get(emotion, (255, 255, 255))
    cv2.putText(frame, f"Émotion : {emotion} ({score:.1f}%)", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

def analyse_emotion_score(frame):
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = DeepFace.analyze(rgb, actions=['emotion'], enforce_detection=False)
        emotions = result[0]['emotion'] if isinstance(result, list) else result['emotion']
        dominant = result[0]['dominant_emotion'] if isinstance(result, list) else result['dominant_emotion']

        if emotions.get('fear', 0) > 20 or emotions.get('angry', 0) > 20 or emotions.get('sad', 0) > 30:
            dominant = 'stressé'
            score = max(emotions.get('fear', 0), emotions.get('angry', 0), emotions.get('sad', 0))
        else:
            score = emotions.get(dominant, 0)

        return dominant, score, emotions
    except Exception as e:
        print(f"[RH] Erreur analyse émotion : {e}")
        return None, 0, {}

def generer_pdf_rapport(id_candidat, nom, prenom, is_same_person, triche, regard_stats):
    os.makedirs(PDF_FOLDER, exist_ok=True)

    i = 1
    while True:
        pdf_path = os.path.join(PDF_FOLDER, f"rapport_{id_candidat}_{i}.pdf")
        if not os.path.exists(pdf_path):
            break
        i += 1

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Rapport d'entretien - {prenom} {nom}", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, f"Identité vérifiée : {'Oui' if is_same_person else 'Non'}", ln=True)
    pdf.cell(200, 10, f"Comportement suspect (triche) : {'Oui' if triche else 'Non'}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Regard détecté :", ln=True)
    for direction, count in regard_stats.items():
        pdf.cell(200, 10, f"- Vers le {direction} : {count} fois", ln=True)
    pdf.output(pdf_path)
    return pdf_path

def enregistrer_rapport_db(id_candidat, nom, prenom, chemin_photo, etat, pdf_path, score):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS rapport_entretien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_candidat TEXT, nom TEXT, prenom TEXT, photo TEXT,
                etat TEXT, rapport_pdf TEXT, score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            INSERT INTO rapport_entretien (id_candidat, nom, prenom, photo, etat, rapport_pdf, score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_candidat, nom, prenom, chemin_photo, etat, pdf_path, score))
        conn.commit()
        conn.close()
        print("[RH] Rapport enregistré avec succès.")
    except Exception as e:
        print(f"[RH] Erreur enregistrement DB : {e}")

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[RH] Webcam non disponible.")
        return

    reference_image = cv2.imread(REFERENCE_IMAGE_PATH)
    if reference_image is None:
        print("[RH] Image de référence introuvable.")
        return

    id_candidat = "CAND123"
    nom, prenom = "Agili", "Manar"
    candidat_reconnu = False
    chemin_photo = ""
    emotion_scores = defaultdict(float)
    emotion_counts = defaultdict(int)

    os.makedirs(PHOTO_SAVE_FOLDER, exist_ok=True)
    print("[CANDIDAT] Démarrage automatique...")

    start_time = time.time()
    emotion_timer = time.time()
    captured = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Webcam", frame)
        key = cv2.waitKey(1) & 0xFF

        if not captured and time.time() - start_time > 2:
            try:
                verification = DeepFace.verify(frame, reference_image, enforce_detection=False)
                if verification.get("verified", False):
                    print("[CANDIDAT] ✅ Visage reconnu.")
                    candidat_reconnu = True
                    chemin_photo = os.path.join(PHOTO_SAVE_FOLDER, f"{id_candidat}_{int(time.time())}.jpg")
                    cv2.imwrite(chemin_photo, frame)
                    captured = True
                else:
                    print("[CANDIDAT] ❌ Visage non reconnu.")
                    break
            except Exception as e:
                print(f"[RH] Erreur vérification : {e}")
                break

        if candidat_reconnu and time.time() - emotion_timer >= 10:
            dom, score, emotions = analyse_emotion_score(frame)
            if dom:
                afficher_emotion(frame, dom, score)
                for k, v in emotions.items():
                    emotion_scores[k] += v
                    emotion_counts[k] += 1

            direction = detecter_regard_direction(frame)
            if direction in regard_directions:
                regard_directions[direction] += 1
                print(f"[CANDIDAT] 👁️ Regard vers : {direction}")
            emotion_timer = time.time()

        if key == ord('q'):
            print("[CANDIDAT] Fin du test.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if not candidat_reconnu:
        return

    if emotion_counts:
        moyennes = {k: emotion_scores[k] / emotion_counts[k] for k in emotion_counts}
        dominant = max(moyennes, key=moyennes.get)
        score_final = moyennes[dominant]
    else:
        dominant, score_final = "inconnu", 0.0

    triche_detectee = sum(regard_directions.values()) >= 5
    pdf_path = generer_pdf_rapport(id_candidat, nom, prenom, candidat_reconnu, triche_detectee, regard_directions)
    enregistrer_rapport_db(id_candidat, nom, prenom, chemin_photo, "Terminé", pdf_path, score_final)

if __name__ == "__main__":
    main()
