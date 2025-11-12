from ursina import *
from game import Game


def main():
    app = Ursina(borderless=False)

    # --- CIELO ---
    sky = Sky(color=color.rgb32(255, 160, 120))

    # --- LUZ AMBIENTAL ---
    ambient = AmbientLight(color=color.rgb32(70, 40, 30))

    # --- SOL ---
    sun = DirectionalLight(shadows=False)
    sun.color = color.rgb32(255, 180, 110)
    sun.look_at(Vec3(0, -0.3, 1))
    sun.shadow_intensity = 0.6
    sun.shadow_resolution = (2048, 2048)

    # Pasamos referencias al juego
    game = Game()
    game.sky = sky
    game.ambient = ambient
    game.sun = sun

    # Día / noche
    game.day_time = 0.95
    game.day_speed = 0.02

    app.run()

if __name__ == "__main__":
    main()