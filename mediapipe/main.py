import cv2
import mediapipe as mp
import socket
import time

HOST = "127.0.0.1"
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

cap = cv2.VideoCapture(0)

# ---- COOLDOWN ----
last_trigger_time = 0
cooldown = 1.0  # segundos

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape  # dimensiones
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    steering = 0
    special_value = None

    # ---- HITBOX MÁS PEQUEÑA ----
    top = 0.2      # antes 0.25
    side = 0.2     # antes 0.25

    if result.pose_landmarks:
        lm = result.pose_landmarks.landmark

        left = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        right = lm[mp_pose.PoseLandmark.RIGHT_WRIST]

        # Coordenadas en píxeles
        rx, ry = int(right.x * w), int(right.y * h)
        lx, ly = int(left.x * w), int(left.y * h)

        # Dibujar puntos
        cv2.circle(frame, (rx, ry), 10, (255, 0, 0), -1)  # derecha
        cv2.circle(frame, (lx, ly), 10, (0, 255, 0), -1)  # izquierda

        # Steering
        steering = (left.y - right.y) * 10

        # ---- ZONAS OBJETIVO (más pequeñas) ----
        zone_y_max = int(top * h)

        # Derecha
        zone_x_min_r = int((1 - side) * w)
        cv2.rectangle(frame, (zone_x_min_r, 0), (w, zone_y_max), (0, 0, 255), 2)

        # Izquierda
        zone_x_max_l = int(side * w)
        cv2.rectangle(frame, (0, 0), (zone_x_max_l, zone_y_max), (0, 255, 255), 2)

        # ---- DETECTAR SOLO SI NO ESTÁ EN COOLDOWN ----
        current_time = time.time()
        if current_time - last_trigger_time >= cooldown:

            # GESTO DERECHA (usando tu condición, pero con hitbox más pequeña)
            left_up = left.y < top
            left_side = left.x > (1 - side)

            if left_up and left_side:
                special_value = 9999
                last_trigger_time = current_time
                cv2.putText(frame, "GESTO DERECHA!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            # GESTO IZQUIERDA
            right_up = right.y < top
            right_side = right.x < side

            if right_up and right_side:
                special_value = 8888
                last_trigger_time = current_time
                cv2.putText(frame, "GESTO IZQUIERDA!", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

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
