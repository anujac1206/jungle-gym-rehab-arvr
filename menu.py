import cv2
import numpy as np
import subprocess
import os

# === Load assets ===
def load_img(path, fallback_shape=(140, 140, 4)):
    if not os.path.exists(path):
        print("Missing image:", path)
        return np.zeros(fallback_shape, dtype=np.uint8)
    return cv2.imread(path, cv2.IMREAD_UNCHANGED)

# Assets
ducky = load_img("assets/ducky.png")
sushi = load_img("assets/fox.png")
chad = load_img("assets/chad.png")
path_bg = load_img("assets/path.png", fallback_shape=(100, 1280, 3))
CHAR_SCALE = (140, 140)
ICON_SCALE = (60, 60)

# Exercise → character icon
exercise_icons = {
    "ducky_pinch": ducky,
    "ducky_fist": ducky,
    "chad_arm_raise": chad,
    "chad_punching": chad,
    "fox_knee_raise": sushi,
    "fox_ankle": sushi,
    "fox_walking": sushi
}

# Overlay PNG
def overlay_png(bg, fg, x, y):
    if fg.shape[2] != 4: return bg
    h, w = fg.shape[:2]
    alpha = fg[:, :, 3] / 255.0
    for c in range(3):
        bg[y:y+h, x:x+w, c] = alpha * fg[:, :, c] + (1 - alpha) * bg[y:y+h, x:x+w, c]
    return bg

# Launch exercise
def launch_exercise(name):
    path = f"{name}.py"
    if os.path.exists(path):
        subprocess.Popen(["python", path], shell=True)
    else:
        err = np.full((300, 600, 3), 240, dtype=np.uint8)
        cv2.putText(err, f"Missing: {path}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
        cv2.imshow("Error", err)
        cv2.waitKey(1500)
        cv2.destroyWindow("Error")

# Conditions ➝ exercises
condition_exercises = {
    "Arthritis (Joint Rehab)": ["ducky_pinch", "ducky_fist", "chad_arm_raise", "fox_knee_raise", "fox_ankle"],
    "Post Knee Surgery (ACL/Meniscus)": ["fox_knee_raise", "fox_walking", "fox_ankle", "chad_arm_raise"],
    "Balance & Fall Prevention Rehab": ["fox_walking", "fox_knee_raise", "fox_ankle", "chad_arm_raise", "duck_pinch"],
    "Ankle Sprain Rehab": ["fox_ankle", "fox_walking", "fox_knee_raise", "chad_arm_raise"],
    "Post-Stroke Recovery": ["ducky_pinch", "ducky_fist", "chad_arm_raise", "chad_punching", "fox_walking", "fox_knee_raise", "fox_ankle"],
    "Parkinsons Disease": ["ducky_pinch", "ducky_fist", "chad_arm_raise", "fox_walking", "fox_knee_raise", "fox_ankle"],
    "Frozen Shoulder": ["chad_arm_raise", "chad_punching", "duck_pinch"],
    "ACL Injury": ["fox_knee_raise", "fox_walking", "fox_ankle", "chad_arm_raise"],
    "Carpal Tunnel": ["ducky_pinch", "ducky_fist", "chad_arm_raise"],
    "Cerebral Palsy": ["ducky_pinch", "ducky_fist", "chad_punching", "fox_knee_raise", "fox_walking", "fox_ankle"]
}

# Show selected condition's exercises
def display_condition_window(condition_name):
    exercises = condition_exercises.get(condition_name, [])
    win_h, win_w = 600, 800
    img = np.full((win_h, win_w, 3), 255, dtype=np.uint8)
    cv2.putText(img, condition_name, (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    positions = []

    for i, ex in enumerate(exercises):
        y = 100 + i * 70
        cv2.rectangle(img, (120, y), (700, y + 50), (230, 255, 230), -1)
        cv2.rectangle(img, (120, y), (700, y + 50), (0, 100, 0), 2)
        cv2.putText(img, ex.replace("_", " ").title(), (190, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
        icon = cv2.resize(exercise_icons.get(ex, np.zeros((60, 60, 4), dtype=np.uint8)), ICON_SCALE)
        overlay_png(img, icon, 130, y - 5)
        positions.append((120, y, 700, y + 50, ex))

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            for (x1, y1, x2, y2, name) in positions:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    try: cv2.destroyWindow("Condition Detail")
                    except: pass
                    launch_exercise(name)

    cv2.namedWindow("Condition Detail")
    cv2.setMouseCallback("Condition Detail", click_event)
    cv2.imshow("Condition Detail", img)
    cv2.waitKey(0)
    try: cv2.destroyWindow("Condition Detail")
    except: pass

# === Main menu loop ===
search_options = list(condition_exercises.keys())
search_active = False
selected_condition = ""

def mouse_event(event, x, y, flags, param):
    global search_active, selected_condition
    if event == cv2.EVENT_LBUTTONDOWN:
        if 300 <= x <= 980 and 110 <= y <= 165:
            search_active = True
        elif search_active:
            for i, item in enumerate(search_options):
                iy = 170 + i * 40
                if 300 <= x <= 980 and iy <= y <= iy + 35:
                    selected_condition = item
                    search_active = False
                    display_condition_window(item)
                    break
            else:
                search_active = False

cv2.namedWindow("Jungle Gym Menu")
cv2.setMouseCallback("Jungle Gym Menu", mouse_event)

while True:
    canvas = np.full((720, 1280, 3), 0, dtype=np.uint8)
    cv2.putText(canvas, "JUNGLE  GYM", (370, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 255), 6)

    # Search bar
    cv2.rectangle(canvas, (300, 110), (980, 165), (255, 255, 255), -1)
    cv2.putText(canvas, selected_condition if selected_condition else "Search by condition...",
                (330, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (10, 10, 10), 2)

    # Optional Tabs
    tabs = ["Arms", "Legs", "Hands"]
    for i, tab in enumerate(tabs):
        x, y = 220 + i * 380, 200
        cv2.rectangle(canvas, (x, y), (x + 350, y + 60), (255, 255, 255), -1)
        cv2.putText(canvas, tab, (x + 20, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)

    # Character cards
    cards = [
        ("Ducky", ducky, (200, 300), (0, 200, 255), ["Egg Pinch", "Make a Fist"]),
        ("Sushi", sushi, (520, 300), (60, 120, 255), ["Walking", "Knee Raise", "Soccer Save"]),
        ("Chad", chad, (840, 300), (80, 200, 100), ["Arm Raise", "Punching"]),
    ]

    for name, img, (cx, cy), col, exs in cards:
        cv2.rectangle(canvas, (cx, cy), (cx + 300, cy + 380), col, -1)
        fg = cv2.resize(img, CHAR_SCALE, interpolation=cv2.INTER_AREA)
        overlay_png(canvas, fg, cx + 80, cy + 20)
        cv2.putText(canvas, name, (cx + 110, cy + 190), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 4)
        for idx, ex in enumerate(exs):
            cv2.putText(canvas, ex, (cx + 30, cy + 250 + idx * 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Dropdown display
    if search_active:
        for i, item in enumerate(search_options):
            iy = 170 + i * 40
            cv2.rectangle(canvas, (300, iy), (980, iy + 35), (255, 255, 255), -1)
            cv2.rectangle(canvas, (300, iy), (980, iy + 35), (0, 0, 0), 1)
            cv2.putText(canvas, item, (310, iy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    # Add path.png beach image at bottom
    if path_bg is not None and path_bg.shape[2] == 4:
        resized_path = cv2.resize(path_bg, (1280, path_bg.shape[0]), interpolation=cv2.INTER_AREA)
        canvas = overlay_png(canvas, resized_path, 0, canvas.shape[0] - resized_path.shape[0])



    cv2.imshow("Jungle Gym Menu", canvas)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
