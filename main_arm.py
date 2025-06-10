# rehab_app/main_arm.py
import cv2
import mediapipe as mp
from exercises.arm import elbow_bend, shoulder_raise

ARM_EXERCISES = [elbow_bend, shoulder_raise]
def run():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
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
        results = pose.process(rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            lm = results.pose_landmarks.landmark
            current_exercise = ARM_EXERCISES[exercise_index]

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
                exercise_index = (exercise_index + 1) % len(ARM_EXERCISES)

            cv2.putText(frame, f"Exercise: {current_exercise.name}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
            cv2.putText(frame, f"Reps: {reps}/10", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (200,200,200), 2)

        cv2.imshow("Arm Rehab Trainer", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
