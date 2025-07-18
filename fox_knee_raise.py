import cv2
import mediapipe as mp
import numpy as np
import time

# Init
cap = cv2.VideoCapture(0)
mp_pose = mp.solutions.pose.Pose()
mp_drawing = mp.solutions.drawing_utils

step_count = 0
target_steps = 10
goal_reached = False
goal_time = None
leg_lifted = False

# Load assets
sushi_img = cv2.imread("assets/fox.png", cv2.IMREAD_UNCHANGED)
ladder_img = cv2.imread("assets/ladder.png", cv2.IMREAD_UNCHANGED)

# Frame dimensions
ret, frame = cap.read()
if not ret:
    print("Error accessing camera")
    exit()
frame_h, frame_w = frame.shape[:2]

# Resize ladder
ladder_width = int(frame_w * 0.2)
ladder_height = frame_h
ladder = cv2.resize(ladder_img, (ladder_width, ladder_height))

# Resize Sushi
sushi_size = int(frame_h * 0.2)
sushi = cv2.resize(sushi_img, (sushi_size, sushi_size))

# Positioning
ladder_x = (frame_w - ladder_width) // 2
sushi_x = (frame_w - sushi_size) // 2
rung_y = [frame_h - int(i * (ladder_height - sushi_size) / (target_steps - 1)) - sushi_size for i in range(target_steps)]
sushi_y = rung_y[0]

# Overlay helper
def overlay_transparent(bg, overlay, x, y):
    h, w = overlay.shape[:2]
    if y + h > bg.shape[0] or x + w > bg.shape[1]:
        return bg
    alpha = overlay[:, :, 3] / 255.0
    for c in range(3):
        bg[y:y+h, x:x+w, c] = alpha * overlay[:, :, c] + (1 - alpha) * bg[y:y+h, x:x+w, c]
    return bg

# Intro popup
ok_button = False
def show_intro():
    dim = cv2.addWeighted(frame.copy(), 0.4, np.zeros_like(frame), 0.6, 0)
    box_w, box_h = 600, 350
    box_x = (frame_w - box_w) // 2
    box_y = (frame_h - box_h) // 2
    cv2.rectangle(dim, (box_x, box_y), (box_x + box_w, box_y + box_h), (50, 50, 50), -1)
    cv2.rectangle(dim, (box_x, box_y), (box_x + box_w, box_y + box_h), (255, 255, 255), 3)

    cv2.putText(dim, "Ladder Hop!", (box_x + 50, box_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

    lines = [
        "Raise your knees one by one",
        "It makes Sushi climb the ladder!",
        "Reach the top in 9 hops to complete.",
        "",
        "Press OK to begin the challenge"
    ]
    for i, line in enumerate(lines):
        cv2.putText(dim, line, (box_x + 40, box_y + 110 + i * 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (230, 230, 230), 2)

    btn_w, btn_h = 160, 50
    btn_x = box_x + (box_w - btn_w) // 2
    btn_y = box_y + box_h - 70
    cv2.rectangle(dim, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (0, 200, 0), -1)
    cv2.putText(dim, "OK", (btn_x + 45, btn_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    return dim, (btn_x, btn_y, btn_w, btn_h)

# Wait for OK
while not ok_button:
    intro, btn = show_intro()
    cv2.imshow("Ladder Hop - Sushi", intro)
    key = cv2.waitKey(1)
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        exit()
    elif key == ord('o'):
        ok_button = True

    def mouse_click(event, x, y, flags, param):
        global ok_button
        bx, by, bw, bh = btn
        if event == cv2.EVENT_LBUTTONDOWN and bx < x < bx + bw and by < y < by + bh:
            ok_button = True
    cv2.setMouseCallback("Ladder Hop - Sushi", mouse_click)

# 🔁 Main Game Loop
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    frame = overlay_transparent(frame, ladder, ladder_x, 0)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_pose.process(rgb)

    if not goal_reached and results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        # Knees and hips
        left_knee = lm[mp.solutions.pose.PoseLandmark.LEFT_KNEE]
        right_knee = lm[mp.solutions.pose.PoseLandmark.RIGHT_KNEE]
        left_hip = lm[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        right_hip = lm[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

        if all(pt.visibility > 0.6 for pt in [left_knee, right_knee, left_hip, right_hip]):
            left_leg_len = abs(left_knee.y - left_hip.y)
            right_leg_len = abs(right_knee.y - right_hip.y)

            left_knee_lift = left_hip.y - left_knee.y
            right_knee_lift = right_hip.y - right_knee.y

            left_ratio = left_knee_lift / left_leg_len if left_leg_len > 0 else 0
            right_ratio = right_knee_lift / right_leg_len if right_leg_len > 0 else 0

            lifted = (left_ratio > 0.4 or right_ratio > 0.4)

            if lifted and not leg_lifted:
                step_count += 1
                if step_count >= target_steps:
                    step_count = target_steps - 1
                sushi_y = rung_y[step_count]
                leg_lifted = True

            elif not lifted:
                leg_lifted = False

            # Draw joint points (green)
            for landmark in [mp.solutions.pose.PoseLandmark.LEFT_KNEE,
                             mp.solutions.pose.PoseLandmark.RIGHT_KNEE,
                             mp.solutions.pose.PoseLandmark.LEFT_HIP,
                             mp.solutions.pose.PoseLandmark.RIGHT_HIP]:
                pt = lm[landmark]
                cx, cy = int(pt.x * frame_w), int(pt.y * frame_h)
                cv2.circle(frame, (cx, cy), 6, (0, 255, 0), -1)

    # Draw Sushi
    frame = overlay_transparent(frame, sushi, sushi_x, sushi_y)

    # Step count
    cv2.putText(frame, f"Steps: {step_count}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 100, 255), 3)

    # Goal message
    if step_count == target_steps - 1 and not goal_reached:
        goal_reached = True
        goal_time = time.time()

    if goal_reached:
        msg = "🎉 Sushi reached the top!"
        font_scale = frame_w / 1000.0
        thickness = int(font_scale * 4)
        (tw, th), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        cx = (frame_w - tw) // 2
        cy = max(th + 20, int(frame_h * 0.15))

        cv2.putText(frame, msg, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)

        if time.time() - goal_time > 3:
            break

    cv2.imshow("Ladder Hop - Sushi", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
