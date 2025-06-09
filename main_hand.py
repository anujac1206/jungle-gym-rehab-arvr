# rehab_app/main_hand.py
import cv2
import mediapipe as mp
from exercises.hand import finger_touch, thumb_touch

HAND_EXERCISES = [finger_touch, thumb_touch]

def run():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    exercise_index = 0
    reps = 0
    performed = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                lm = hand_landmarks.landmark
                current_exercise = HAND_EXERCISES[exercise_index]

                if current_exercise.is_done(lm):
                    cv2.putText(frame, "✅ Good form!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)
                    if not performed:
                        reps += 1
                        performed = True
                else:
                    performed = False
                    cv2.putText(frame, f"❌ {current_exercise.name}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

                if reps >= 10:
                    reps = 0
                    exercise_index = (exercise_index + 1) % len(HAND_EXERCISES)

                cv2.putText(frame, f"Exercise: {current_exercise.name}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
                cv2.putText(frame, f"Reps: {reps}/10", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (200,200,200), 2)

        cv2.imshow("Hand Rehab Trainer", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
