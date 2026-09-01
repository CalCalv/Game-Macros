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
import requests
import random

pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0

runningTinytasks = []

#File Path finding
def getScriptDir():
    return os.path.dirname(os.path.abspath(__file__))

def getImagePath(imageName):
    return os.path.join(getScriptDir(), "pictures", imageName)

def getTinytaskPath(tinytaskName):
    return os.path.join(getScriptDir(), "exe", tinytaskName)

def loadImageUrl(url):
    response = requests.get(url)
    imageBytes = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(imageBytes, cv2.IMREAD_GRAYSCALE)
    return image

#Tinytask
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

#Emergency Exit
def escListener():
    keyboard.wait('esc')
    print("\nEscape key pressed! Killing TinyTask and exiting now...")
    killTinytaskProcesses()
    os._exit(0)

threading.Thread(target=escListener, daemon=True).start()

#Image stuff
class ImageTimeoutError(Exception):
    pass

def templateCreation(name ,type):
    if type == "url": 
        template = loadImageUrl(name)
    elif type == "file":
        imagePath = getImagePath(name)
        template = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print("Could not load image")
    else:
        raise ValueError(f"Unknown source_type: {type}")
    return template

def locateImage(imageName, type, region=None, confidence=0.7):
    """
    Locate an image on screen
    """
    template = templateCreation(imageName,type)

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

def waitForImage(imageName, type , confidence=0.7, checkInterval=0.05, timeout=30, region=None):
    """
    Wait until the image appears on screen
    """
    imagePath = getImagePath(imageName)
    print(f"Waiting for image: {imagePath} (timeout: {timeout}s)...")
    startTime = time.time()
    while True:
        location = locateImage(imagePath, type, region=region, confidence=confidence)
        if location:
            print(f"Image found at: {location}")
            return location
        if time.time() - startTime > timeout:
            raise ImageTimeoutError(f"Timeout: {imagePath} not found after {timeout} seconds.")
        time.sleep(checkInterval)

# Mouse clicks

def click(*args):
    if args is None:
        return
    if len(args) == 1:
        obj = args[0]
        if isinstance(obj,dict):
            x = obj["left"]
            y = obj["top"]
        elif isinstance(obj,(tuple,list)):
            x , y = obj
        else:
            raise ValueError("1 arg wrong")
    elif(len(args)==2):
        x = args[0]
        y = args[1]
    else:
        raise ValueError("click() expects either 1 or 2 arguments")
    
    x += random.randint(-3, 3)
    y += random.randint(-3, 3)

    duration = random.uniform(0.001, 0.005)

    pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)

    time.sleep(random.uniform(0.05, 0.15))

    pyautogui.click()

    time.sleep(1)


#Main

topNode = (1082,111)
middleNode = (1082,420)
bottomNode = (1082,750)
Nodes = {topNode,middleNode,bottomNode}
choice1Button = (1299,368)

def enterDungeon():
    clicks = [
    (1471, 944, 1),
    (642, 465, 3),
    (1065, 722, 1),
    (1065, 722, 1),
    (1711, 876, 1),
    (1065, 722, 1.5),
    (1760, 1000, 1.5),
    (1065, 822, 1),
    (537, 353, 1),
    (1475, 383, 1),
    (1633, 869, 1),
    (967, 802, 1),
    (1330, 864, 1),
    (1112, 740, 1)
    ]
    for x, y, delay in clicks:
        click(x, y)
        time.sleep(delay)

def openPack(): 
    duration = random.uniform(0.005, 0.01)
    pyautogui.moveTo(950,330,duration=duration, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(1)
    pyautogui.dragTo(950,700,duration=duration, tween = pyautogui.easeInOutQuad)

def chooseNode():
    for node in Nodes:
        click(node)
        location = locateImage("enter.png","file")
        if location:
            click(location)
            return

def nodeId():
    if locateImage("battleIndicator.png","file"):
        click(1714,881)
        time.sleep(15)
        battle()
    elif locateImage("occuranceIndicator.png","file"):
        occurance()
    else:
        shop()
        
            
def battle():
    click(1900,1060)
    while(locateImage("battleEnd.png","file") is None):
        if locateImage("winRate.png","file"):
            pyautogui.doubleClick()
            time.sleep(.5)
            keyboard.press_and_release('p')
            time.sleep(.5)
            keyboard.press_and_release('enter')
        time.sleep(.5)
        if(locateImage("occuranceIndicator.png","file")):
            occurance()
    time.sleep(10)
    rewards()
    time.sleep(1)
    rewards()

def rewards():
    if locateImage("encounterReward.png","file"):
        click(1075,500)
        click(1150,800)
        click(locateImage("confirm.png","file"))
    if locateImage("gift.png","file"):
        click(locateImage("gift.png","file"))
        click(locateImage("select.png","file"))
    if (locateImage("confirm.png","file")):
        click(locateImage("confirm.png","file"))

def proceedCheck():
    if (locateImage("proceed.png","file")):
        click(locateImage("proceed.png","file"))

def spamClick():
    pyautogui.moveTo(choice1Button,duration = random.uniform(0.005, 0.01), tween=pyautogui.easeInOutQuad) 
    for n in range(30):    
        pyautogui.click()
        time.sleep(.2)

oddsList = ("veryHigh.png","high.png","normal.png","low.png","veryLow.png")

def sinnerCheck():
    if (locateImage("sinners.png","file")):
        for odds in oddsList:
            if locateImage(odds,"file"):
                click(locateImage(odds,"file"))
                click(locateImage("commence.png","file"))
                return
        

def occurance():
    while(locateImage("continue.png","file") is None):
        spamClick()
        proceedCheck()
        spamClick()
        sinnerCheck()
        spamClick()
    click(locateImage("continue.png","file"))
    time.sleep(1)
    rewards()
    if(locateImage("winRate.png","file")):
        battle()
    
    
def shop():
    click(locateImage("leave.png","file"))
    click(1127,740)

def end():
    time.sleep(1)
    if (locateImage("confirm.png","file")):
        click(locateImage("confirm.png","file"))
    click(locateImage("claim1.png","file"))
    click(locateImage("claim2.png","file"))
    click(1134,739)
    click(locateImage("confirm.png","file"))


    
def floor():
    while not (locateImage("packs.png","file")):
        chooseNode()
        time.sleep(1)
        nodeId()
        

def run():
    time.sleep(1)
    enterDungeon()
    time.sleep(1)
    for n in range(5):
        time.sleep(2)
        openPack()
        time.sleep(3)
        floor() 
    end()

def main():
    for n in range(5):
        run()

main()