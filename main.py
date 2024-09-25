import cv2
import math
import numpy as np
from PIL import ImageGrab
import pyautogui
from time import sleep, time
from random import randint
import keyboard

# Define color ranges
lower_red = np.array([0, 145, 74])
upper_red = np.array([7, 255, 255])
# lower_red = np.array([163, 145, 74])
# upper_red = np.array([187, 255, 255])
lower_green = np.array([43, 155, 111])
upper_green = np.array([63, 255, 255])

"""
#states
0 not fishing
1 start fishing
2 dragging the fish
"""

pyautogui.FAILSAFE = False

start_x, start_y, end_x, end_y = [None]*4


def get_cords():
    global start_x, start_y, end_x, end_y
    while (True):
        a = keyboard.read_key()

        if a == '1':
            start_x, start_y = pyautogui.position()
        elif a == '2':
            end_x, end_y = pyautogui.position()
        if all([start_x, start_y, end_x, end_y]):
            break


def main():
    global start_x, start_y, end_x, end_y
    mouse = "down"
    state = 0
    prev_red_mask = None
    while True:
        try:
            if state == 0:
                
                x = start_x+(end_x-start_x)//2
                y = start_y+(end_y-start_y)//2
                pyautogui.moveTo(x=x, y=y)
                sleep(2.2)
                pyautogui.mouseDown(x=x, y=y)
                dist = int(math.hypot(x - 960, y - 540))
                sleep(randint(dist-5, dist+5)/1000)
                pyautogui.mouseUp(x=x, y=y)
                pyautogui.moveTo(x=x+100, y=y+100)
                sleep(1)
                state = 1
                continue
            
            # bbox specifies the region (bbox=left, top, right, bottom)
            screen = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))
            # Crop the screen to the box region
            fish_spot = screen[start_y:end_y, start_x:end_x]
            left_progress = screen[545:555, 900:910]
            right_progress = screen[545:555, 1035:1045]

            # Convert the image to HSV color space
            red_mask = cv2.inRange(cv2.cvtColor(
                fish_spot, cv2.COLOR_RGB2HSV), lower_red, upper_red)
            left_mask = cv2.inRange(cv2.cvtColor(
                left_progress, cv2.COLOR_RGB2HSV), lower_green, upper_green)
            right_mask = cv2.inRange(cv2.cvtColor(
                right_progress, cv2.COLOR_RGB2HSV), lower_green, upper_green)
            
            
            if prev_red_mask is None:
                prev_red_mask = red_mask
                continue

            if np.count_nonzero(cv2.bitwise_and(prev_red_mask, red_mask) == 255) < np.count_nonzero(red_mask == 255)//2 and state == 1:
                print("caught fish")
                pyautogui.mouseDown()
                state = 2
                mouse = "down"
                sleep(0.4)
                continue

            prev_red_mask = red_mask
            if state == 2:
                if np.count_nonzero(right_mask == 255) < 5 and np.count_nonzero(left_mask == 255) < 5:
                    pyautogui.mouseUp()
                    print("finished fishing")
                    state = 0
                    prev_red_mask = None
                    continue

                if np.count_nonzero(left_mask == 255) < 20 and mouse == "up":
                    print("holding mouse")
                    pyautogui.mouseDown()
                    mouse = "down"
                    sleep(0.1)
                    continue
                
                if np.count_nonzero(right_mask == 255) < 20 and mouse == "down":
                    print("releasing mouse")
                    pyautogui.mouseUp()
                    mouse = "up"
                    sleep(0.1)
                    print("holding mouse")
                    pyautogui.mouseDown()
                    mouse = "down"
                    continue

        except Exception as e:
            print(e)

        # Break the loop if 'q' is 
        if keyboard.is_pressed("q"):
            cv2.destroyAllWindows()
            exit(0)


if __name__ == "__main__":
    print("Script Started, Getting rectangle coords...")
    get_cords()
    main()
    
