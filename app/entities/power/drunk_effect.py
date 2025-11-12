from ursina import *
import random, time


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
