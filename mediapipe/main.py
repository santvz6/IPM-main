import cv2
import mediapipe as mp
import socket
import time


# Socket
HOST = "127.0.0.1"
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# cv2
cap = cv2.VideoCapture(0)


# MediaPipe logic
last_trigger_time = 0
cooldown = 1.0  # trigger cooldown (seconds)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape  # dimensions
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    steering = 0
    special_value = None

    # Square Hitbox
    top_right = 0.2    
    side_right = 0.2   

    top_left = 0.3    
    side_left = 0.4    


    if result.pose_landmarks:
        lm = result.pose_landmarks.landmark

        left = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        right = lm[mp_pose.PoseLandmark.RIGHT_WRIST]

        # Pixel coordinates
        rx, ry = int(right.x * w), int(right.y * h)
        lx, ly = int(left.x * w), int(left.y * h)

        # Joint Circle Draw
        cv2.circle(frame, (rx, ry), 10, (255, 0, 0), -1)  # right
        cv2.circle(frame, (lx, ly), 10, (0, 255, 0), -1)  # left

        # Rectangle Area Zone Draw
        right_zone_y_max = int(top_right * h)
        right_zone_x_min = int((1 - side_right) * w)
        cv2.rectangle(frame, (right_zone_x_min, 0), (w, right_zone_y_max), (0, 0, 255), 2)

        left_zone_y_max = int(top_left * h)
        left_zone_x_max = int(side_left * w)
        cv2.rectangle(frame, (0, 0), (left_zone_x_max, left_zone_y_max), (0, 255, 255), 2)

        # Only Detects if it is NOT in Cooldown
        current_time = time.time()
        if current_time - last_trigger_time >= cooldown:

            # Right Detection
            left_up = left.y < top_right
            left_side = left.x > (1 - side_right)

            if left_up and left_side:
                special_value = 9999
                last_trigger_time = current_time
                cv2.putText(frame, "GESTO DERECHA!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            # Left detection
            right_up = right.y < top_left and left.y < top_left
            right_side = right.x < side_left and left.x < side_left

           

            if (right_up and right_side):
                special_value = 8888
                last_trigger_time = current_time
                cv2.putText(frame, "GESTO IZQUIERDA!", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    # Steering Value
    steering = (left.y - right.y) * 10

    # ---- ENVIAR ----
    if special_value is not None:
        print("GESTO DETECTADO →", special_value)
        message = f"{special_value}".encode()
    else:
        print("steering:", steering)
        message = f"{steering}".encode()

    sock.sendto(message, (HOST, PORT))

    cv2.imshow("Camara", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

    time.sleep(0.01)

cap.release()
cv2.destroyAllWindows()
