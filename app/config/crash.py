# crash.py
from ursina import *
import random

class Crash:
    def __init__(self, game, duration=5):
        self.game = game
        self.duration = duration
        self.timer = 0
        self.active = False

        # Overlay negro
        self.overlay = Entity(parent=camera.ui, model="quad", scale=(2,2), color=color.rgba32(0,0,0,0))
        self.text = Text(parent=camera.ui, scale=1, origin=(0,0), color=color.red, enabled=False)
        
        

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt

        # Jugador sin movimiento
        self.game.player.speed = 0

        # Movimiento errático del coche
        self.game.player.x += (random.random() - 0.5) * 0.2
        self.game.player.y += (random.random() - 0.5) * 0.1
        self.game.player.rotation_y += (random.random() - 0.5) * 10
        self.game.player.rotation_z += (random.random() - 0.5) * 10

        # Oscurecer pantalla
        alpha = min(self.timer / self.duration, 1)
        self.overlay.color = color.rgba32(0,0,0,int(alpha*255))

        # Hacer que el texto crezca suavemente
        self.text.enabled = True
        self.text.text = f"TE HAS ESTRELLADO\n{(self.game.player.z*10**-2):.0f}m"
        self.text.scale = lerp(self.text.scale, Vec3(3, 3, 3), dt * 2)


        if self.timer >= self.duration:
            self.active = False
            self.game_over()

    def game_over(self):
        application.quit()
