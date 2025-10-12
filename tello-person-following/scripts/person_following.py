import time
import cv2
import numpy as np
from djitellopy import tello

IMG_WIDTH, IMG_HEIGHT = 360, 240
ALLOWED_AREA_RANGE = (10000, 12000)  # Min and max area 
PID_VALUES = [0.4, 0.4, 0]

drone = tello.Tello()
drone.connect()
print(drone.get_battery())

# # Initialize the drone
drone.streamon()
drone.takeoff()
drone.send_rc_control(0, 0, 20, 0) # Ascend a bit
time.sleep(3)


def detect_bodies_dnn(frame, net, conf_threshold=0.5):
    (h, w) = frame.shape[:2]

    # Prepare input blob for the network
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)),
        scalefactor=0.007843,  # 1/127.5
        size=(300, 300),
        mean=127.5
    )
    net.setInput(blob)
    detections = net.forward()

    centers, areas, boxes = [], [], []

    # Loop over detections
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            class_id = int(detections[0, 0, i, 1])

            # COCO class ID for "person" = 15
            if class_id == 15:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")
                x, y, w_box, h_box = x1, y1, x2 - x1, y2 - y1

                boxes.append((x, y, w_box, h_box))
                centers.append((x + w_box // 2, y + h_box // 2))
                areas.append(w_box * h_box)

    return boxes, centers, areas


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
    
    cap = cv2.VideoCapture(0)
    net = cv2.dnn.readNetFromCaffe(
        "resources/mobilenet_ssd_deploy.prototxt",
        "resources/mobilenet_ssd.caffemodel"
    )

    while True:
        # _, frame = cap.read()
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))

        bodies, centers, areas = detect_bodies_dnn(frame, net)
        frame = draw_detections(frame, bodies, centers)

        center, area = get_largest_body(centers, areas)
        if len(bodies):
            print(f"Detected bodies: {len(bodies)}, Largest area: {area}, Center: {center}")

        # Control
        fb, yaw, cur_error = track_face(center, area, IMG_WIDTH, prev_error)
        prev_error = cur_error
        if fb or yaw:
            print(f"Control commands - Forward/Backward: {fb}, Yaw: {yaw}, Error: {cur_error}")
            drone.send_rc_control(0, fb, 0, yaw)

        # Display frame
        cv2.imshow('Webcam', frame)

        # Exit on ESC key
        if cv2.waitKey(1) == 27:
            drone.land()
            break

    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
