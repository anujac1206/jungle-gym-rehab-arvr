import numpy as np
import cv2
from transparent import *
from gamebuttons import *
import subprocess 

logo= cv2.imread('Assets/logo.png',cv2.IMREAD_UNCHANGED)
logo=cv2.resize(logo,(400,200))
cap=cv2.VideoCapture(0)

success,frame=cap.read()
if not success:
    print("Camera not working")
    cap.release()
    exit()

frame_h,frame_w=frame.shape[:2]

# Define buttons
button1 = Button("Finger Thumb Exercise", (int((frame_w-600)/2), int((frame_h-100)/2)), (600, 100))
button2 = Button("Fist Exercise",(int((frame_w-600)/2), int((frame_h-100)/2)+250), (600, 100))
# Click handling
def mouse_callback(event, x, y,flags, param):
    if event == cv2.EVENT_LBUTTONDOWN: #left click
        if button1.is_clicked(x, y):
            subprocess.Popen(["python3", "game1.py"])
        elif button2.is_clicked(x, y):
            subprocess.Popen(["python3", "game2.py"])

cv2.namedWindow("Welcome to the game ducky")  
cv2.setMouseCallback("Welcome to the game ducky", mouse_callback)

while True:
    success,frame=cap.read()

    if not success:
        break
    frame=cv2.flip(frame,1)
    
    logo_h,logo_w=logo.shape[:2]
    x_logo=int((frame_w-logo_w)/2)
    y_logo=frame_h-logo_h-700
    frame=overlay_transparent(frame,logo,x_logo,y_logo)
    # Draw buttons
    button1.draw(frame)
    button2.draw(frame)


    cv2.imshow("Welcome to the game ducky",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()


