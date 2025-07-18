import cv2
import numpy as np
import random

class EggManager:
    def __init__(self,egg_image,frame_width,frame_height,num_eggs=3):
        self.egg_image = egg_image
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.eggs = []
        self.num_eggs = num_eggs
        self.init_eggs()

    def init_eggs(self):
        for _ in range(self.num_eggs):
            x = random.randint(0, self.frame_width - self.egg_image.shape[1])
            y=0
            speed = 3  # Vary speed for more realism
            self.eggs.append({'x': x, 'y': y, 'speed': speed})


    def update_eggs(self):#gives access to all variables
        for i in self.eggs:
            i["y"]+=i["speed"]
            if i["y"]>self.frame_height:
                i["y"]=0
                i["x"] = random.randint(0, self.frame_width - self.egg_image.shape[1])
                i["speed"] = 3
    
    
    
    
    def draw_eggs(self, frame, overlay_func):
        for egg in self.eggs:
            x=int(egg['x'])
            y=int(egg['y'])
            frame = overlay_func(frame, self.egg_image, x, y)
        return frame