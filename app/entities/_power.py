# entities/power/power.py
from ursina import *
from ursina.shaders import lit_with_shadows_shader

class _Power(Entity):
    def __init__(self, game, model="cube", position=(0,0,0), scale=1, rotation=0):
        super().__init__(
            model=model,
            position=position,
            scale=scale,
            rotation=rotation,
            shader=lit_with_shadows_shader
        )
        self.game = game
        self.elapsed = 0

    def floating_animation(self):
        self.elapsed += time.dt
        self.y += math.sin(self.elapsed * 2) * 0.002   # suave y no explosivo

    def update(self):
        self.floating_animation()

    def try_activate(self):
        pass  # implementado en subconclases
