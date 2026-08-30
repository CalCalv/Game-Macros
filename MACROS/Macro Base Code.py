import pyautogui
import time
import subprocess
import keyboard
import threading
import os
import sys
import PIL
import mss
import cv2
import numpy as np
import position

runningTinytasks = []

# -------- PATH HELPERS -------- #
def getScriptDir():
    return os.path.dirname(os.path.abspath(__file__))

def getImagePath(imageName):
    return os.path.join(getScriptDir(), "pictures", imageName)

def getTinytaskPath(tinytaskName):
    return os.path.join(getScriptDir(), "exe", tinytaskName)

# -------- TINYTASK CONTROL -------- #
def startTinytask(tinytaskName):
    exePath = getTinytaskPath(tinytaskName)
    proc = subprocess.Popen([exePath])
    runningTinytasks.append(proc)
    print(f"Started TinyTask with PID: {proc.pid}")
    return proc

def killTinytaskProcesses():
    print("Killing all tracked TinyTask processes...")
    for proc in runningTinytasks:
        try:
            proc.terminate()
            if proc.poll() is None:
                proc.kill()
            print(f"Killed TinyTask process PID: {proc.pid}")
        except Exception as e:
            print(f"Error killing process: {e}")
    runningTinytasks.clear()

# -------- ESCAPE LISTENER -------- #
def escListener():
    keyboard.wait('esc')
    print("\nEscape key pressed! Killing TinyTask and exiting now...")
    killTinytaskProcesses()
    os._exit(0)

threading.Thread(target=escListener, daemon=True).start()

# -------- IMAGE LOGIC -------- #
class ImageTimeoutError(Exception):
    pass

def locateImage(imagePath, region=None, confidence=0.7):
    """
    Locate an image on screen
    """
    template = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"Template image not found: {imagePath}")
        return None
    templateWidth, templateHeight = template.shape[::-1]

    with mss.mss() as sct:
        if region:
            monitor = {
                "top": region[1],
                "left": region[0],
                "width": region[2],
                "height": region[3]
            }
        else:
            monitor = sct.monitors[0]  # full screen

        screenshot = np.array(sct.grab(monitor))
        grayScreenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        matchResult = cv2.matchTemplate(grayScreenshot, template, cv2.TM_CCOEFF_NORMED)
        matchLocations = np.where(matchResult >= confidence)
        points = list(zip(*matchLocations[::-1]))

        if points:
            x, y = points[0]
            return {
                "left": x + (region[0] if region else 0),
                "top": y + (region[1] if region else 0),
                "width": templateWidth,
                "height": templateHeight
            }
        return None

def waitForImage(imageName, confidence=0.7, checkInterval=0.05, timeout=30, region=None):
    """
    Wait until the image appears on screen
    """
    imagePath = getImagePath(imageName)
    print(f"Waiting for image: {imagePath} (timeout: {timeout}s)...")
    startTime = time.time()
    while True:
        location = locateImage(imagePath, region=region, confidence=confidence)
        if location:
            print(f"Image found at: {location}")
            return location
        if time.time() - startTime > timeout:
            raise ImageTimeoutError(f"Timeout: {imagePath} not found after {timeout} seconds.")
        time.sleep(checkInterval)

# -------- CONTROLS -------- #
def smoothHoverClick(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click()
    pyautogui.click()