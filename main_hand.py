# rehab_app/main_hand.py
import cv2
import mediapipe as mp
from exercises.hand.fingertouch import finger_touch
from exercises.hand.thumbtouch import thumb_touch

HAND_EXERCISES = [finger_touch, thumb_touch]

def run():
    print(f"Loaded Exercises: {[ex.name for ex in HAND_EXERCISES]}")

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    exercise_index = 0
    reps = 0
    performed = False

    while exercise_index < len(HAND_EXERCISES):
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        current_exercise = HAND_EXERCISES[exercise_index]

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                lm = hand_landmarks.landmark

                if current_exercise.is_done(lm):
                    cv2.putText(frame, "✅ Good form!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)
                    if not performed:
                        reps += 1
                        performed = True
                        print(f"[{current_exercise.name}] Rep: {reps}")
                else:
                    performed = False
                    cv2.putText(frame, f"❌ {current_exercise.name}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

        cv2.putText(frame, f"Exercise: {current_exercise.name}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
        cv2.putText(frame, f"Reps: {reps}/10", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (200,200,200), 2)

        if reps >= 10:
            print(f"✅ Completed {current_exercise.name}")
            reps = 0
            exercise_index += 1
            performed = False
            if exercise_index < len(HAND_EXERCISES):
                next_ex = HAND_EXERCISES[exercise_index].name
                print(f"➡️ Moving to next exercise: {next_ex}")
                cv2.putText(frame, f"Next: {next_ex}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                cv2.imshow("Hand Rehab Trainer", frame)
                cv2.waitKey(2000)

        cv2.imshow("Hand Rehab Trainer", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    print("All hand exercises completed ✅")
    cap.release()
    cv2.destroyAllWindows()
