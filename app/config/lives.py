from ursina import *

class Lives:
    def __init__(self, game, heart_texture, max_lives=3, start_pos=(-0.85, 0.45), scale=0.05, spacing=0.06, invuln_time=0.5):
        self.game = game        

        self.max_lives = max_lives
        self.current_lives = max_lives
        self.invulnerable = False
        self.invuln_time = invuln_time
        self.heart_texture = heart_texture
        self.hearts = []

        # Crear sprites de corazón
        for i in range(max_lives):
            heart = Entity(
                parent=camera.ui,
                model='quad',
                texture=self.heart_texture,
                scale=scale,
                position=(start_pos[0] + i * spacing, start_pos[1], 0),
            )
            self.hearts.append(heart)

    def lose_life(self):
        if self.current_lives <= 0 or self.invulnerable:
            return

        self.current_lives -= 1
        self.update_ui()
        self.start_invulnerability()

        if self.current_lives <= 0:
            self.game_over()

    def add_life(self, amount=1):
        self.current_lives = min(self.current_lives + amount, self.max_lives)
        self.update_ui()

    def update_ui(self):
        # Activar/desactivar los sprites según la vida actual
        for i, heart in enumerate(self.hearts):
            heart.enabled = i < self.current_lives

    def start_invulnerability(self):
        self.invulnerable = True
        invoke(self.end_invulnerability, delay=self.invuln_time)

    def end_invulnerability(self):
        self.invulnerable = False

    def game_over(self):
        # Llamamos a la función de descontrol en Game
        self.game.start_crash_sequence()
