from djitellopy import tello
import cv2

drone = tello.Tello()
drone.connect()
print(drone.get_battery())

drone.streamon()

while True:
    frame = drone.get_frame_read().frame
    frame = cv2.resize(frame, (360, 240)) # Resize for faster processing
    cv2.imshow("Tello Camera", frame)
    key = cv2.waitKey(1)