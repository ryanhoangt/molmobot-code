import time
import cv2
import numpy as np
from djitellopy import tello

IMG_WIDTH, IMG_HEIGHT = 360, 240
ALLOWED_AREA_RANGE = (600, 800)  # Min and max area 
PID_VALUES = [0.4, 0.4, 0]

drone = tello.Tello()
drone.connect()
print(drone.get_battery())

# Initialize the drone
drone.streamon()
drone.takeoff()
drone.send_rc_control(0, 0, 10, 0) # Ascend a bit
time.sleep(3)


def detect_bodies(frame, cascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bodies = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    centers, areas = [], []
    for (x, y, w, h) in bodies:
        centers.append((x + w // 2, y + h // 2))
        areas.append(w * h)
    return bodies, centers, areas


def draw_detections(frame, bodies, centers):
    for (x, y, w, h), center in zip(bodies, centers):
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, center, 5, (255, 0, 0), cv2.FILLED)
    return frame


def get_largest_body(centers, areas):
    if not areas:
        return (0, 0), 0
    idx = np.argmax(areas)
    return centers[idx], areas[idx]


def track_face(center, area, cam_width, prev_error):
    # Forward/backward
    fb = 0
    if area > ALLOWED_AREA_RANGE[1]:
        fb = -20
    elif area < ALLOWED_AREA_RANGE[0] and area != 0:
        fb = 20
    
    # Yaw
    if center[0] == 0:
        yaw = 0
        err = 0
    else:
        err = center[0] - cam_width // 2
        yaw_speed = PID_VALUES[0] * err + PID_VALUES[1] * (err - prev_error)
        yaw = int(np.clip(yaw_speed, -100, 100))

    return fb, yaw, err


def main():
    prev_error = 0
    
    # cap = cv2.VideoCapture(0)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        # _, frame = cap.read()
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))

        bodies, centers, areas = detect_bodies(frame, cascade)
        frame = draw_detections(frame, bodies, centers)

        center, area = get_largest_body(centers, areas)
        if len(bodies):
            print(f"Detected bodies: {len(bodies)}, Largest area: {area}, Center: {center}")

        # Control
        fb, yaw, cur_error = track_face(center, area, IMG_WIDTH, prev_error)
        prev_error = cur_error
        # print(f"Control commands - Forward/Backward: {fb}, Yaw: {yaw}, Error: {cur_error}")
        if fb or yaw:
            drone.send_rc_control(0, fb, 0, yaw)

        # Display frame
        cv2.imshow('Webcam', frame)

        # Exit on ESC key
        if cv2.waitKey(1) == 27:
            drone.land()
            break

    
    # cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()