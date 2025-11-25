import cv2
import mediapipe as mp
import socket
import time

# ------------------------------------------------------------
# Configuración del socket
# ------------------------------------------------------------
HOST = "127.0.0.1"
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ------------------------------------------------------------
# Inicializamos MediaPipe Pose
# ------------------------------------------------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# ------------------------------------------------------------
# Inicializamos la cámara
# ------------------------------------------------------------
cap = cv2.VideoCapture(0)

# ------------------------------------------------------------
# Variables de control del sistema
# ------------------------------------------------------------
ultimo_disparo = 0
cooldown = 1.0  # Tiempo mínimo entre activaciones de gestos

# ------------------------------------------------------------
# Bucle principal
# ------------------------------------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Invertimos el frame para que el movimiento sea más natural
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Procesamos con MediaPipe (requiere RGB)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    steering = 0
    special_value = None

    # Zonas de detección definidas en valores normalizados
    zona_der_top = 0.2
    zona_der_side = 0.2

    zona_izq_top = 0.3
    zona_izq_side = 0.4

    # ------------------------------------------------------------
    # Procesamos landmarks si MediaPipe detectó el cuerpo
    # ------------------------------------------------------------
    if result.pose_landmarks:
        lm = result.pose_landmarks.landmark

        # Obtenemos las muñecas
        left = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        right = lm[mp_pose.PoseLandmark.RIGHT_WRIST]

        # Convertimos coordenadas normalizadas a píxeles
        lx, ly = int(left.x * w), int(left.y * h)
        rx, ry = int(right.x * w), int(right.y * h)

        # Dibujamos ambas muñecas para depuración visual
        cv2.circle(frame, (rx, ry), 10, (255, 0, 0), -1)
        cv2.circle(frame, (lx, ly), 10, (0, 255, 0), -1)

        # Dibujamos zona derecha
        der_y_max = int(zona_der_top * h)
        der_x_min = int((1 - zona_der_side) * w)
        cv2.rectangle(frame, (der_x_min, 0), (w, der_y_max), (0, 0, 255), 2)

        # Dibujamos zona izquierda
        izq_y_max = int(zona_izq_top * h)
        izq_x_max = int(zona_izq_side * w)
        cv2.rectangle(frame, (0, 0), (izq_x_max, izq_y_max), (0, 255, 255), 2)

        ahora = time.time()

        # Solo detectamos gestos si pasó el cooldown
        if ahora - ultimo_disparo >= cooldown:

            # Comprobamos gesto hacia la derecha:
            # La mano izquierda debe estar arriba y a la derecha
            mano_izq_arriba = left.y < zona_der_top
            mano_izq_derecha = left.x > (1 - zona_der_side)

            if mano_izq_arriba and mano_izq_derecha:
                special_value = 9999
                ultimo_disparo = ahora
                cv2.putText(frame, "GESTO DERECHA!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            # Comprobamos gesto hacia la izquierda:
            # Ambas manos deben estar arriba y hacia la izquierda
            manos_arriba = right.y < zona_izq_top and left.y < zona_izq_top
            manos_izquierda = right.x < zona_izq_side and left.x < zona_izq_side

            if manos_arriba and manos_izquierda:
                special_value = 8888
                ultimo_disparo = ahora
                cv2.putText(frame, "GESTO IZQUIERDA!", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        # Calculamos el steering a partir de la diferencia de alturas
        steering = (left.y - right.y) * 10

    # ------------------------------------------------------------
    # Envío del valor por UDP
    # ------------------------------------------------------------
    if special_value is not None:
        print("Gesto detectado ->", special_value)
        mensaje = f"{special_value}".encode()
    else:
        print("steering:", steering)
        mensaje = f"{steering}".encode()

    sock.sendto(mensaje, (HOST, PORT))

    # Mostramos la ventana de la cámara
    cv2.imshow("Camara", frame)

    # Salimos si presionamos ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

    # Pequeño delay para evitar saturar la CPU
    time.sleep(0.01)

# ------------------------------------------------------------
# Liberamos recursos al salir
# ------------------------------------------------------------
cap.release()
cv2.destroyAllWindows()
