import cv2
import numpy as np
import mediapipe as mp
import random
import time

# Init
cap = cv2.VideoCapture(0)
mp_pose = mp.solutions.pose.Pose()
mp_draw = mp.solutions.drawing_utils

# Load assets
sushi_img = cv2.imread("assets/fox.png", cv2.IMREAD_UNCHANGED)
ball_img = cv2.imread("assets/soccer_ball.png", cv2.IMREAD_UNCHANGED)
goal_img = cv2.imread("assets/goal_net.png", cv2.IMREAD_UNCHANGED)

# Check
if sushi_img is None or ball_img is None or goal_img is None:
    print("❌ One or more assets missing.")
    exit()

# Frame size
ret, frame = cap.read()
if not ret:
    print("❌ Camera error.")
    exit()
frame_h, frame_w = frame.shape[:2]

# Resize assets
goal_img = cv2.resize(goal_img, (frame_w, int(frame_h * 0.6)))
goal_net_height = goal_img.shape[0]
goal_top_y = frame_h - goal_net_height

ball_size = int(frame_h * 0.1)
ball_img = cv2.resize(ball_img, (ball_size, ball_size))

sushi_size = int(frame_h * 0.3)
sushi_img = cv2.resize(sushi_img, (sushi_size, sushi_size))

# Sushi position (lowered to 93% of goal)
sushi_bottom_y = goal_top_y + int(goal_net_height * 0.93)
sushi_y = sushi_bottom_y - sushi_size
sushi_x = (frame_w - sushi_size) // 2

# Overlay
def overlay_transparent(bg, overlay, x, y):
    h, w = overlay.shape[:2]
    if x >= bg.shape[1] or y >= bg.shape[0]:
        return bg
    if x + w > bg.shape[1]:
        w = bg.shape[1] - x
        overlay = overlay[:, :w]
    if y + h > bg.shape[0]:
        h = bg.shape[0] - y
        overlay = overlay[:h]
    if overlay.shape[2] < 4:
        return bg
    alpha = overlay[:, :, 3] / 255.0
    for c in range(3):
        bg[y:y+h, x:x+w, c] = (alpha * overlay[:, :, c] +
                               (1 - alpha) * bg[y:y+h, x:x+w, c])
    return bg

# Ball class
class Ball:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.randint(50, frame_w - ball_size - 50)
        self.y = 0
        self.speed = random.randint(6, 10)
    def update(self):
        self.y += self.speed
    def draw(self, frame):
        overlay_transparent(frame, ball_img, self.x, self.y)
    def hit_sushi(self):
        return (self.y + ball_size >= sushi_y) and (self.x + ball_size//2 in range(sushi_x, sushi_x + sushi_size))

# Intro popup
ok_button = False
def show_intro(frame):
    dim = cv2.addWeighted(frame.copy(), 0.4, np.zeros_like(frame), 0.6, 0)
    box_w, box_h = 600, 300
    box_x = (frame_w - box_w) // 2
    box_y = (frame_h - box_h) // 2
    cv2.rectangle(dim, (box_x, box_y), (box_x + box_w, box_y + box_h), (30, 30, 30), -1)
    cv2.rectangle(dim, (box_x, box_y), (box_x + box_w, box_y + box_h), (255, 255, 255), 2)
    cv2.putText(dim, "Soccer Save!", (box_x + 120, box_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
    lines = [
        "Tilt your ankle left or right to move Sushi.",
        "Block the soccer balls coming to the goal!",
        "Save 10 balls to finish the game.",
        "",
        "Click OK to start"
    ]
    for i, line in enumerate(lines):
        cv2.putText(dim, line, (box_x + 40, box_y + 110 + i * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (230, 230, 230), 2)
    btn_w, btn_h = 160, 50
    btn_x = box_x + (box_w - btn_w) // 2
    btn_y = box_y + box_h - 70
    cv2.rectangle(dim, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (0, 200, 0), -1)
    cv2.putText(dim, "OK", (btn_x + 45, btn_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    return dim, (btn_x, btn_y, btn_w, btn_h)

def click_ok(event, x, y, flags, param):
    global ok_button
    bx, by, bw, bh = param
    if event == cv2.EVENT_LBUTTONDOWN and bx < x < bx + bw and by < y < by + bh:
        ok_button = True

# Show popup first
while not ok_button:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    popup, btn_coords = show_intro(frame)
    cv2.imshow("Soccer Save - Sushi", popup)
    cv2.setMouseCallback("Soccer Save - Sushi", click_ok, btn_coords)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cap.release()
        cv2.destroyAllWindows()
        exit()

# Game loop
ball = Ball()
score = 0
goal_reached = False
goal_time = None
sushi_shift = 0

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)

    # Detect from clean frame
    clean = frame.copy()
    rgb = cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)
    results = mp_pose.process(rgb)

    ankles_visible = False
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        l_ankle = lm[mp.solutions.pose.PoseLandmark.LEFT_ANKLE]
        r_ankle = lm[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE]
        if l_ankle.visibility > 0.6 and r_ankle.visibility > 0.6:
            ankles_visible = True
            lx, rx = int(l_ankle.x * frame_w), int(r_ankle.x * frame_w)
            cx = (lx + rx) // 2
            sushi_shift = cx - frame_w // 2
            sushi_x = int(frame_w // 2 + sushi_shift - sushi_size // 2)

            # Show ankles
            ly = int(l_ankle.y * frame_h)
            ry = int(r_ankle.y * frame_h)
            cv2.circle(frame, (lx, ly), 10, (0, 255, 0), -1)
            cv2.circle(frame, (rx, ry), 10, (0, 255, 0), -1)

    # Draw goal net after detection
    frame[-goal_net_height:, :] = overlay_transparent(frame[-goal_net_height:, :], goal_img, 0, 0)

    # Draw Sushi
    frame = overlay_transparent(frame, sushi_img, sushi_x, sushi_y)

    # Ball logic
    if ankles_visible:
        if not goal_reached:
            ball.update()
            if ball.hit_sushi():
                score += 1
                ball.reset()
            elif ball.y > frame_h:
                ball.reset()
        ball.draw(frame)

    # Score
    cv2.putText(frame, f"Saves: {score}/10", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 100, 255), 3)

    # Win message
    if score >= 10 and not goal_reached:
        goal_reached = True
        goal_time = time.time()

    if goal_reached:
        msg = "Great job! You saved them all!"
        (tw, th), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)
        cx = (frame_w - tw) // 2
        cy = int(frame_h * 0.4)
        cv2.putText(frame, msg, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
        if time.time() - goal_time > 3:
            break

    cv2.imshow("Soccer Save - Sushi", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
