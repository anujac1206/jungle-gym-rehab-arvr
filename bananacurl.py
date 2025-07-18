import cv2
import mediapipe as mp
import numpy as np
from transparent import overlay_transparent
import math

# Load assets
chad_img = cv2.imread("assets/chad.png", cv2.IMREAD_UNCHANGED)
banana_img = cv2.imread("assets/banana_dumbbell.png", cv2.IMREAD_UNCHANGED)

# Mediapipe setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Helper to calculate angle at the elbow
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return angle if angle <= 180 else 360 - angle

# Game state
rep_count = 0
curling_right = False
curling_left = False

# Camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    frame_h, frame_w = frame.shape[:2]
    display = frame.copy()

    # Resize and position Chad in bottom-right
    chad = cv2.resize(chad_img, (int(frame_w * 0.2), int(frame_h * 0.4)))
    chad_x = frame_w - chad.shape[1]
    chad_y = frame_h - chad.shape[0]
    display = overlay_transparent(display, chad, chad_x, chad_y)

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        # --- RIGHT ARM ---
        r_shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame_w,
                      lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame_h]
        r_elbow = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * frame_w,
                   lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * frame_h]
        r_wrist = [lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * frame_w,
                   lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * frame_h]
        r_index = [lm[mp_pose.PoseLandmark.RIGHT_INDEX.value].x * frame_w,
                   lm[mp_pose.PoseLandmark.RIGHT_INDEX.value].y * frame_h]
        r_pinky = [lm[mp_pose.PoseLandmark.RIGHT_PINKY.value].x * frame_w,
                   lm[mp_pose.PoseLandmark.RIGHT_PINKY.value].y * frame_h]

        angle_r = calculate_angle(r_shoulder, r_elbow, r_wrist)

        if angle_r < 50 and not curling_right:
            rep_count += 1
            curling_right = True
        elif angle_r > 100 and curling_right:
            curling_right = False

        # Palm center = average of wrist, index base, pinky base
        r_palm_x = int((r_wrist[0] + r_index[0] + r_pinky[0]) / 3)
        r_palm_y = int((r_wrist[1] + r_index[1] + r_pinky[1]) / 3)

        banana_r = cv2.resize(banana_img, (200, 200))
        bw_r, bh_r = banana_r.shape[1], banana_r.shape[0]
        bx_r = r_palm_x - bw_r // 2
        by_r = r_palm_y - bh_r // 2

        if 0 <= bx_r <= frame_w - bw_r and 0 <= by_r <= frame_h - bh_r:
            display = overlay_transparent(display, banana_r, bx_r, by_r)

        # --- LEFT ARM ---
        l_shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame_w,
                      lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame_h]
        l_elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * frame_w,
                   lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * frame_h]
        l_wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x * frame_w,
                   lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y * frame_h]
        l_index = [lm[mp_pose.PoseLandmark.LEFT_INDEX.value].x * frame_w,
                   lm[mp_pose.PoseLandmark.LEFT_INDEX.value].y * frame_h]
        l_pinky = [lm[mp_pose.PoseLandmark.LEFT_PINKY.value].x * frame_w,
                   lm[mp_pose.PoseLandmark.LEFT_PINKY.value].y * frame_h]

        angle_l = calculate_angle(l_shoulder, l_elbow, l_wrist)

        if angle_l < 50 and not curling_left:
            rep_count += 1
            curling_left = True
        elif angle_l > 100 and curling_left:
            curling_left = False

        # Palm center = average of wrist, index base, pinky base
        l_palm_x = int((l_wrist[0] + l_index[0] + l_pinky[0]) / 3)
        l_palm_y = int((l_wrist[1] + l_index[1] + l_pinky[1]) / 3)

        banana_l = cv2.resize(banana_img, (200, 200))
        bw_l, bh_l = banana_l.shape[1], banana_l.shape[0]
        bx_l = l_palm_x - bw_l // 2
        by_l = l_palm_y - bh_l // 2

        if 0 <= bx_l <= frame_w - bw_l and 0 <= by_l <= frame_h - bh_l:
            display = overlay_transparent(display, banana_l, bx_l, by_l)

    # Display Score & Instructions
    font_scale = frame_w / 1000
    cv2.putText(display, f"Reps: {rep_count}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                font_scale + 0.5, (255, 255, 255), 2)
    cv2.putText(display, "Curl either arm to lift banana-bells!",
                (30, frame_h - 30), cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (0, 255, 0), 2)

    # Show game window
    cv2.imshow("Banana Curl Brawl - Dual Arm Mode", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
