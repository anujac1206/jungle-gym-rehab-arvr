# 🧠 Jungle Gym AR/VR - Gamified Physical Therapy for Rehabilitation & Recovery

Jungle Gym is an immersive AR/VR rehabilitation experience that uses computer vision (MediaPipe) and colorful pixel art characters to guide users through fun, therapeutic exercises. Designed especially for patients recovering from injuries or managing physical conditions, Jungle Gym blends therapy with interaction, motivation, and play.

## 🌟 Features

- Gesture-based main menu and navigation (no mouse/keyboard)
- Themed interactive environment with pixel animals:  
  🐥 Ducky → Fingers  
  🦊 Sushi → Legs  
  🐵 Chad → Arms  
-  tap to **select**,
- Full camera-based overlay system (MediaPipe)
- AR/VR-based exercise selection by body part or condition
- Visual feedback, cute animations, and motivational UI
- Custom Jungle Gym theme with colorful UI tabs

---

## 🎮 Exercise Games Included

| Character | Exercises |
|----------|-----------|
| 🐥 Ducky (Fingers & Hands) | Egg Pinch, Pop the Bubbles, Feather Flick |
| 🐵 Chad (Wrists & Arms) | Magic Wand, Duck Dash, Balloon Race |
| 🦊 Sushi (Shoulders to Legs) | Rainbow Reach, Posture Hero, Turtle Walk, Ladder Hop, Soccer Save, etc. |
| 🦉 Neck/Head | Owl Watch, Balloon Balance |

Each exercise uses MediaPipe landmarks and visual overlays for feedback and interaction.

---

## 🧰 Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/jungle-gym-arvr.git
   cd jungle-gym-arvr
   ```

2. Install dependencies using `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the main menu:
   ```bash
   python menu.py
   ```

Make sure your camera is active and unobstructed.

---

## 📦 Dependencies

Listed in `requirements.txt`, including:
- `mediapipe`
- `opencv-python`
- `pygame`
- `Pillow`
- `numpy`

---

## 📁 Project Structure

```
├── menu.py                  # AR Menu with gesture support
├── fox_ankle.py             # Soccer Save game
├── ducky_fingers.py         # Ducky's hand exercise game
├── chad_arms.py             # Chad's arm/wrist game
├── assets/
│   ├── characters/          # Pixel art for Ducky, Sushi, Chad
│   ├── backgrounds/         # Jungle Gym UI + beach, ladder, goal, etc.
│   └── sound/               # Clicks, feedback, ambient sounds
├── requirements.txt
├── README.md
```

---

## 🎯 Use Cases

- Post-surgery rehab
- Pediatric therapy
- Stroke recovery
- Home-based physiotherapy with no special hardware

---

## 👩‍⚕️ Built For

- Patients
- Therapists
- Rehab Clinics
- Gamified HealthTech Enthusiasts

---


## 🤝 Contributing

Feel free to fork and extend this. If you design new character-based games or themes, submit a pull request.

---

