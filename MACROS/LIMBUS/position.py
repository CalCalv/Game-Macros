import pyautogui
import time
import subprocess
import keyboard
import threading
import os
import sys
import pynput
from pynput import mouse

class Point:
    x=0
    y=0

def getPositionOnClick():
    def on_click(x, y, button, pressed):
        if pressed:
            x,y = pyautogui.position()
            print(f"X: {x}, Y: {y}")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    
def getPosition():
    x,y = pyautogui.position()
    print(f"x: {x}, Y: {y}")
    
    

def positionDiff():
    positions = []

    def on_click(x, y, button, pressed):
        if pressed:
            positions.append((x, y))
            if len(positions) == 2:
                # Stop listener after 2 clicks
                return False

    # Start listening for mouse clicks
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # Calculate difference
    x_diff = positions[1][0] - positions[0][0]
    y_diff = positions[1][1] - positions[0][1]

    print(f"x: {positions[0][0]}, Y: {positions[0][1]}")
    print(f"W: {x_diff}, H: {y_diff}")
