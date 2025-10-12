from djitellopy import tello
from time import sleep

import utils.keypress as kp

kp.init()
drone = tello.Tello()
drone.connect()
print(drone.get_battery())

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

    if kp.get_key("q"): drone.land(); sleep(3); exit()
    elif kp.get_key("e"): drone.takeoff()

    return [lr, fb, ud, yv]

while True:
    vals = get_keyboard_input()
    drone.send_rc_control(*vals)
    sleep(0.05)