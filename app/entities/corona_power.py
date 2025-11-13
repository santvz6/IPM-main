from ._power import _Power
from ursina import *

import random, os, time


class CoronaPower(_Power):
    def __init__(self, game, position, scale, rotation):
        super().__init__(
            game,
            position=position,
            model=random.choice(os.listdir("app/assets/models/powers")),
            scale=scale,
            rotation=rotation,
        )
        self.activated = False

    def try_activate(self):
        if self.activated:
            return 
        
        # steering especial del jugador
        if self.game.player.steering == 9999:
            self.activated = True
            print("¡Poder Corona obtenido!")
            self.on_pickup()

    def on_pickup(self):
        # Guardamos la velocidad original
        original_speed = self.game.player.speed

        self.game.player.speed *= 1.5
        camera.fov = 100

        # Hacer que la botella sea hija de la cámara
        self.parent = camera
        self.position = Vec3(0.0, -0.5, 2)  # frente a la cámara
        self.rotation = Vec3(0, 0, 0)       # vertical
        self.scale = Vec3(0.4, 0.2, 0.4)    # tamaño visible

        # Duraciones
        drink_duration = 0.6   # inclinación inicial
        hold_duration = 0.8    # tiempo sosteniendo la botella inclinada
        toss_duration = 0.8    # tiempo para tirar la botella
        drunk_duration = 15     # duración total del efecto borracho

        # --- FASE 1: inclinar y acercar ---
        self.animate_rotation(Vec3(-120, 0, 0), duration=drink_duration, curve=curve.linear)
        self.animate_position(Vec3(0.3, -0.3, 1.5), duration=drink_duration, curve=curve.linear)
        
        # --- FASE 2: mantener inclinada ---
        def hold_bottle():
            self.animate_position(Vec3(0.3, -0.2, 1.5), duration=hold_duration, curve=curve.linear)
        invoke(hold_bottle, delay=drink_duration)

        # --- FASE 3: tirar hacia un lado ---
        def toss_bottle():
            self.animate_position(Vec3(1.5, -0.5, 3), duration=toss_duration, curve=curve.linear)
            self.animate_rotation(Vec3(-180, 0, 90), duration=toss_duration, curve=curve.linear)
            self.animate_scale(Vec3(0,0,0), duration=toss_duration, curve=curve.linear)
            invoke(destroy, self, delay=toss_duration)
        invoke(toss_bottle, delay=drink_duration + hold_duration)

        # --- EFECTO BORRACHO ---
        def start_drunk_effect():
            # Creamos la instancia de DrunkEffect con duración deseada
            DrunkEffect(duration=drunk_duration)

            # Restaurar la velocidad después de la duración
            def restore_state():
                self.game.player.speed = original_speed
                camera.fov = 90
            invoke(restore_state, delay=drunk_duration)


            # --- Alteraciones aleatorias del jugador ---
            def alter_player():
                t = time.time() - start_time
                if t > drunk_duration:
                    return  # fin del efecto

                # Cambios aleatorios
                self.game.player.x += random.uniform(-0.5, 0.5)   # lateral
                self.game.player.speed += random.uniform(-0.1, 0.1)      # velocidad temporal
                
                # Repetir cada 0.1 segundos
                invoke(alter_player, delay=0.1)

            start_time = time.time()
            alter_player()

        invoke(start_drunk_effect, delay=drink_duration)  # empieza cuando empieza a beber


class DrunkEffect(Entity):
    """Efectos de borracho: blur, shake y luces estilo policía"""
    def __init__(self, duration=10, shake_intensity=0.05):
        super().__init__()

        self.duration = duration
        self.shake_intensity = shake_intensity
        self.active = True  # para detener el loop de luces

        # --- Blur frente a la cámara ---
        self.blur = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(255,255,255,0.5),
            scale=(2,2)
        )

        # --- Police lights ---
        self.overlay = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2,2),
            color=color.rgba(255,0,0,0.1)
        )

        # --- Shake ---
        self.start_time = time.time()
        self._shake_camera()

        # --- Empieza parpadeo ---
        self._flash_red()

        # --- Finaliza efecto después de duración ---
        invoke(self.end_effect, delay=self.duration)

    # --- Shake de cámara ---
    def _shake_camera(self):
        if not self.active:
            return
        t = time.time() - self.start_time
        if t > self.duration:
            camera.position = Vec3(0, 1.5, 0)  # reset
            return
        camera.position = Vec3(
            0 + random.uniform(-self.shake_intensity,self.shake_intensity),
            1.5 + random.uniform(-self.shake_intensity,self.shake_intensity),
            0
        )
        invoke(self._shake_camera, delay=0.016)  # ~60 FPS

    # --- Police lights rojo / azul ---
    def _flash_red(self):
        if not self.active:
            return
        self.overlay.color = color.rgba(255,0,0,0.1)
        invoke(self._flash_blue, delay=0.2)

    def _flash_blue(self):
        if not self.active:
            return
        self.overlay.color = color.rgba(0,0,255,0.1)
        invoke(self._flash_red, delay=0.2)

    # --- Terminar efecto ---
    def end_effect(self):
        self.active = False
        camera.position = Vec3(0, 1.5, 0)  # reset
        destroy(self.blur)
        destroy(self.overlay)
        destroy(self)
