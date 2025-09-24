from djitellopy import tello
import cv2
from time import sleep

drone = tello.Tello()
drone.connect()
print(drone.get_battery())

drone.stream_on()

while True:
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (360, 240)) # Resize for faster processing
    cv2.imshow("Tello Camera", frame)
    key = cv2.waitKey(1)