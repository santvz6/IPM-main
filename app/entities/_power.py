# entities/power/power.py
from ursina import *

class _Power(Entity):
    def __init__(self, game, model="cube", position=(0,0,0), scale=1, rotation=0):
        super().__init__(
            model=model,
            position=position,
            scale=scale,
            rotation=rotation
        )
        self.game = game
        self.elapsed = 0

    def floating_animation(self):
        self.elapsed += time.dt
        self.y += math.sin(self.elapsed * 2) * 0.002   # suave y no explosivo

    def update(self):
        self.floating_animation()

        # Si el jugador está cerca, intenta activarse
        if distance(self.position, self.game.player.position) < 2:
            self.try_activate()

    def try_activate(self):
        pass  # implementado en subconclases
