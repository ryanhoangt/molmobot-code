from djitellopy import tello
import time
import cv2
import os

import utils.keypress as kp

kp.init()
drone = tello.Tello()
drone.connect()
print(drone.get_battery())

drone.streamon()

def get_keyboard_input():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50
    
    if kp.get_key("LEFT"): lr = -speed
    elif kp.get_key("RIGHT"): lr = speed
    elif kp.get_key("UP"): fb = speed
    elif kp.get_key("DOWN"): fb = -speed

    if kp.get_key("w"): ud = speed
    elif kp.get_key("s"): ud = -speed
    elif kp.get_key("a"): yv = -speed
    elif kp.get_key("d"): yv = speed

    if kp.get_key("q"): drone.land(); time.sleep(3); exit()
    elif kp.get_key("e"): drone.takeoff()

    if kp.get_key("z"):
        os.makedirs("resources/imgs", exist_ok=True) # Ensure directory exists
        cv2.imwrite(f"resources/imgs/{time.time()}.jpg", frame)
        time.sleep(0.3) # Prevent multiple captures

    return [lr, fb, ud, yv]

while True:
    vals = get_keyboard_input()
    drone.send_rc_control(*vals)

    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (360, 240)) # Resize for faster processing
    cv2.imshow("Tello Camera", frame)
    cv2.waitKey(1)