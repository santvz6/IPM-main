from ursina import *

class LeaveCar:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.progress = 0
        self.duration = 2   # animación más rápida, estilo "salto"
        
        self.original_cam_parent = None
        self.original_cam_pos = None

        self.walk_timer = 0   # para el efecto caminar

    def on_activate(self):
        if self.active:
            return
        
        print("Jugador SALTA por la ventana izquierda")
        self.active = True
        self.progress = 0
        
        self.game.difficulty.level_interval /= 15
        self.game.difficulty._max_enemies = int(self.game.difficulty._max_enemies * 1.6)

        # Guardar parámetros originales
        self.original_cam_rot = camera.rotation
        self.original_cam_pos = camera.position


    def update(self, dt):
        if (self.game.player.steering == 8888 or held_keys["l"]) and not self.active:
            self.on_activate()

        if not self.active:
            return

        self.progress += dt / self.duration
        t = min(self.progress, 1.0)

        # -------------------------
        # Movimiento del salto (cámara)
        # -------------------------
        exit_rot = Vec3(
            self.original_cam_rot.x,
            self.original_cam_rot.y,
            self.original_cam_rot.z - 30
        )
        if t < 0.5:
            cam_t = t / 0.5
            camera.rotation = lerp(self.original_cam_rot, exit_rot, cam_t)
            self.game.steerwheel.rotation = lerp(self.original_cam_rot, -exit_rot, cam_t)
            self.game.dashboard.rotation = lerp(self.original_cam_rot, -exit_rot, cam_t)

        else:
            cam_t = max(0.0, min((t - 0.5) / 0.15, 1.0))
            camera.rotation = lerp(exit_rot, self.original_cam_rot, cam_t)
            

        # -------------------------
        # MOVIMIENTO DEL COCHE
        # -------------------------

        # 1) El coche se desplaza a la derecha cuando sales
        car_right_offset = 1.4     # cuanto se mueve a la derecha
        self.game.steerwheel.x = lerp(0, car_right_offset, t)
        self.game.dashboard.x = lerp(0, car_right_offset, t)

        # 2) El coche se aleja ligeramente hacia adelante
        car_forward_offset = -4.5   # distancia de alejamiento
        self.game.steerwheel.z = lerp(0, car_forward_offset, t)
        self.game.dashboard.z = lerp(0, car_forward_offset, t)


        # ------------------------- 
        # Fin de animación
        # -------------------------
        if t >= 1.0:
            camera.rotation = self.original_cam_rot


         # -------------------------
        # EFECTO CAMINAR (HEAD-BOB)
        # -------------------------
        self.walk_timer += dt * 11   # velocidad del movimiento
        bob_amount = 0.08          # amplitud del movimiento
        camera.y = self.original_cam_pos.y + math.sin(self.walk_timer) * bob_amount
