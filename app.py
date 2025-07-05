import cv2
from deepface import DeepFace
import time
from collections import defaultdict

REFERENCE_IMAGE_PATH = "C:/Users/HP/Downloads/facial-analysis-service/test_image22.jpg"

# Couleurs pour affichage selon émotion (BGR)
emotion_colors = {
    'angry': (0, 0, 255),       # Rouge
    'disgust': (0, 128, 0),     # Vert foncé
    'fear': (128, 0, 128),      # Violet
    'happy': (0, 255, 255),     # Jaune
    'sad': (255, 0, 0),         # Bleu
    'surprise': (0, 165, 255),  # Orange
    'neutral': (255, 255, 255), # Blanc
    'stressé': (0, 0, 128)      # Rouge foncé pour stress (cas spécial)
}

def analyse_emotion_score(frame):
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
        if isinstance(result, list):
            emotions = result[0]['emotion']
            dominant_emotion = result[0]['dominant_emotion']
        else:
            emotions = result['emotion']
            dominant_emotion = result['dominant_emotion']

        # Détecter "stressé" par seuils sur peur, colère ou tristesse
        if emotions.get('fear', 0) > 20 or emotions.get('angry', 0) > 20 or emotions.get('sad', 0) > 30:
            dominant_emotion = 'stressé'

        score = emotions.get(dominant_emotion, 0) if dominant_emotion != 'stressé' else max(
            emotions.get('fear', 0), emotions.get('angry', 0), emotions.get('sad', 0)
        )

        return dominant_emotion, score, emotions
    except Exception as e:
        print(f"Erreur analyse émotion : {e}")
        return None, 0, {}

def afficher_emotion(frame, emotion, score):
    color = emotion_colors.get(emotion, (255, 255, 255))
    text = f"Emotion: {emotion} ({score:.1f}%)"
    cv2.putText(frame, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

def main():
    reference_image = cv2.imread(REFERENCE_IMAGE_PATH)
    if reference_image is None:
        print("❌ Erreur : Impossible de lire l'image de référence.")
        return

    cap = cv2.VideoCapture(0)
    compatible = False
    emotion_timer_started = False
    last_emotion_time = 0
    emotion_scores_cumule = defaultdict(float)
    emotion_counts = defaultdict(int)

    print("Appuyez sur 's' pour capturer et comparer la photo")
    print("Appuyez sur 'q' pour quitter")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erreur capture webcam")
            break

        cv2.imshow("Webcam", frame)
        key = cv2.waitKey(1)

        if key & 0xFF == ord('s'):
            print("📸 Photo capturée, comparaison en cours...")
            try:
                verification = DeepFace.verify(frame, reference_image, enforce_detection=False)
                compatible = verification['verified']
                if compatible:
                    print("✅ Personne reconnue, démarrage de l’analyse des émotions.")
                    emotion_timer_started = True
                    last_emotion_time = time.time()

                    emotion, score, _ = analyse_emotion_score(frame)
                    if emotion:
                        afficher_emotion(frame, emotion, score)
                        cv2.imshow("Webcam", frame)

                        # Stocker résultats pour statistiques
                        emotion_scores_cumule[emotion] += score
                        emotion_counts[emotion] += 1
                else:
                    print("❌ Personne non reconnue.")
                    emotion_timer_started = False
            except Exception as e:
                print(f"Erreur comparaison : {e}")
                compatible = False
                emotion_timer_started = False

        if compatible and emotion_timer_started:
            current_time = time.time()
            if current_time - last_emotion_time >= 10:
                ret, frame = cap.read()
                if not ret:
                    print("Erreur capture webcam pendant analyse émotion")
                    break

                emotion, score, _ = analyse_emotion_score(frame)
                if emotion:
                    afficher_emotion(frame, emotion, score)
                    cv2.imshow("Webcam", frame)

                    emotion_scores_cumule[emotion] += score
                    emotion_counts[emotion] += 1
                else:
                    print("⚠️ Aucune émotion détectée.")
                last_emotion_time = current_time

        if key & 0xFF == ord('q'):
            print("👋 Fin du programme.")
            break

    # Affichage résumé des émotions moyennes à la fin
    if emotion_counts:
        print("\n📊 Résumé des émotions moyennes pendant l'entretien :")
        for emo in emotion_scores_cumule:
            moyenne = emotion_scores_cumule[emo] / emotion_counts[emo]
            print(f" - {emo}: {moyenne:.1f}% (basé sur {emotion_counts[emo]} analyses)")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
