# rehab_app/exercises/hand/fingertouch.py
import cv2

class FingerTouchExercise:
    def __init__(self):
        self.name = "Finger Touch with Ball Pickup"
        self.ball_pos = (300, 300)
        self.box_pos = (100, 100)
        self.ball_radius = 20
        self.held = False

    def is_done(self, landmarks):
        # Index finger tip: id = 8
        # Thumb tip: id = 4
        index = landmarks[8]
        thumb = landmarks[4]

        dist = ((index.x - thumb.x) ** 2 + (index.y - thumb.y) ** 2) ** 0.5
        screen_x = int(index.x * 640)
        screen_y = int(index.y * 480)

        # Simulate ball pick up when fingers are close near ball
        if dist < 0.05 and not self.held:
            if abs(screen_x - self.ball_pos[0]) < self.ball_radius and abs(screen_y - self.ball_pos[1]) < self.ball_radius:
                self.held = True
                self.ball_pos = (screen_x, screen_y)
                return False

        # Move the ball with finger while held
        if self.held:
            self.ball_pos = (screen_x, screen_y)

            # Check if inside box
            bx, by = self.box_pos
            if bx < screen_x < bx + 60 and by < screen_y < by + 60:
                self.held = False  # Drop the ball
                return True

        return False

    def draw(self, frame):
        # Draw the box
        cv2.rectangle(frame, self.box_pos, (self.box_pos[0]+60, self.box_pos[1]+60), (0, 255, 0), 2)

        # Draw the ball
        color = (0, 0, 255) if not self.held else (255, 0, 0)
        cv2.circle(frame, self.ball_pos, self.ball_radius, color, -1)

# The export name
finger_touch = FingerTouchExercise()
