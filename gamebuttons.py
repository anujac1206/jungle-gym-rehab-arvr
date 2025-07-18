import cv2

class Button:
    def __init__(self, text, position, size, color=(0, 120, 255), text_color=(255, 255, 255)):
        self.text = text
        self.position = position  # (x, y)
        self.size = size          # (width, height)
        self.color = color
        self.text_color = text_color

    def draw(self, frame):
        x, y = self.position
        w, h = self.size
        cv2.rectangle(frame, (x, y), (x + w, y + h), self.color, -1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(self.text, font, 1, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(frame, self.text, (text_x, text_y), font, 1, self.text_color, 2)

    def is_clicked(self, mouse_x, mouse_y):
        x, y = self.position
        w, h = self.size
        return x <= mouse_x <= x + w and y <= mouse_y <= y + h
