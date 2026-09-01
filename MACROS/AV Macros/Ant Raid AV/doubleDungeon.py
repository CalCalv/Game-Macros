import pyautogui
import time
import subprocess
import keyboard
import threading
import os
import sys
from pyautogui import ImageNotFoundException

# Path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(*parts):
    """Join path parts relative to the script directory."""
    return os.path.join(BASE_DIR, *parts)

#Tinytasks
running_tinytasks = []

def kill_tinytask_processes():
    print("Killing all TinyTask processes.")
    for proc in running_tinytasks:
        try:
            proc.terminate()
            time.sleep(0.2)
            if proc.poll() is None:
                proc.kill()
        except Exception as e:
            print(f"Error")
    running_tinytasks.clear()

#emergenci exit
def esc_listener():
    keyboard.wait('esc')
    print("\nExiting")
    kill_tinytask_processes()
    os._exit(0)

threading.Thread(target=esc_listener, daemon=True).start()

def run_tinytask(exe_path):
    proc = subprocess.Popen([exe_path])
    running_tinytasks.append(proc)
    return proc

#mouse
def smooth_hover_click(target_x, target_y):
    pyautogui.moveTo(target_x, target_y)
    pyautogui.click()
    pyautogui.click()


#image logic
def safe_locate(image_path, confidence=0.7, region=None):
    try:
        return pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
    except ImageNotFoundException:
        return None
    except Exception as e:
        print(f"Error searching for {image_path}: {e}")
        return None

def find_click_or_reset(image_path, tiny_task_path, confidence=0.8, check_interval=0.1):
    try:
        while True:
            if retry(get_path("pictures", "retry.png"), 0.7):
                print("Retrying")

            location = safe_locate(image_path, confidence)
            if location:
                print(f"Image found at: {location}")
                center = pyautogui.center(location)
                run_tinytask(get_path("exe", "swtich.exe")).wait()
                time.sleep(.5)
                smooth_hover_click(center.x, center.y)
                time.sleep(check_interval)
                return
            else:
                print("Image not found. Reseting.")
                run_tinytask(tiny_task_path).wait()
                cancel(get_path("pictures", "cancel.png"))
                print("Reset complete.")
                time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\nExiting")
        kill_tinytask_processes()
        sys.exit(0)

def wait_for_image(image_path, confidence=0.7, check_interval=0.1):
    print(f"Waiting for image: {image_path}...")
    while True:
        location = safe_locate(image_path, confidence)
        if location:
            print(f"Image found at: {location}")
            return
        time.sleep(check_interval)

def priority_image_click(image_list, confidence=0.5, check_interval=0.2):
    try:
        while True:
            for image_path in image_list:
                location = safe_locate(image_path, confidence, region=[200, 200, 1200, 500])
                if location:
                    print(f"Found image: {image_path} at {location}")
                    center = pyautogui.center(location)
                    run_tinytask(get_path("exe", "swtich.exe")).wait()
                    smooth_hover_click(center.x, center.y)
                    return
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\nExiting")
        kill_tinytask_processes()
        sys.exit(0)

def retry(image_path, confidence):
    location = safe_locate(image_path, confidence)
    if location:
        print(f"Retry image found at: {location}")
        while True:
            location = safe_locate(image_path, confidence)
            if not location:
                print("Retry image not found")
                break

            center = pyautogui.center(location)
            run_tinytask(get_path("exe", "swtich.exe")).wait()
            smooth_hover_click(center.x, center.y)
            run_tinytask(get_path("exe", "swtich.exe")).wait()
            smooth_hover_click(center.x, center.y)
            time.sleep(0.3)

            while cancel(get_path("pictures", "cancel.png"), confidence):
                time.sleep(0.3)
        return True
    else:
        return False

def cancel(secondary_image_path, confidence=0.7):
    location = safe_locate(secondary_image_path, confidence)
    if location:
        print(f"Cancel image found at: {location}")
        center = pyautogui.center(location)
        run_tinytask(get_path("exe", "swtich.exe")).wait()
        smooth_hover_click(center.x, center.y)
        return True
    else:
        return False


image_list = [
    get_path("pictures", "harvest.png"),
    get_path("pictures", "uncommonloot.png"),
    get_path("pictures", "commonloot.png"),
    get_path("pictures", "damage2.png"),
    get_path("pictures", "range2.png"),
    get_path("pictures", "spa2.png"),
    get_path("pictures", "slayer2.png"),
    get_path("pictures", "damage1.png"),
    get_path("pictures", "spa1.png"),
    get_path("pictures", "range1.png"),
    get_path("pictures", "slayer1.png"),
    get_path("pictures", "press.png"),
    get_path("pictures", "champions.png"),
    get_path("pictures", "speed.png"),
    get_path("pictures", "dodge.png"),
    get_path("pictures", "plan.png"),
    get_path("pictures", "precise.png"),
    get_path("pictures", "strong.png"),
]

def phase_routine(exe_file):
    while cancel(get_path("pictures", "cancel.png")):
        time.sleep(0.3)
    if retry(get_path("pictures", "retry.png"), 0.7):
        print("Retry")
        return False
    wait_for_image(get_path("pictures", "cards.png"), 0.5)
    priority_image_click(image_list, 0.7)
    run_tinytask(exe_file).wait()
    time.sleep(1)
    return True 

def run():
    restart = get_path("exe", "restart.exe")

    while True:
        while cancel(get_path("pictures", "cancel.png")):
            time.sleep(0.3)
        if retry(get_path("pictures", "retry.png"), 0.7):
            continue

        find_click_or_reset(get_path("pictures", "exterminator.png"), restart)
        run_tinytask(get_path("exe", "3.exe")).wait()
        time.sleep(2)

        for exe_file in [
            get_path("exe", "6.exe"),
            get_path("exe", "9.exe"),
            get_path("exe", "12.exe"),
            get_path("exe", "15.exe"),
            get_path("exe", "18.exe"),
            get_path("exe", "21.exe"),
            get_path("exe", "24.exe"),
            get_path("exe", "27.exe"),
            get_path("exe", "30.exe"),
            get_path("exe", "end.exe"),
        ]:
            if not phase_routine(exe_file):
                print("Restarting cycle.")
                break
        else:
            print("Cycle complete, restarting..q.")

run()
