# enemy.py

from ursina import *
from ursina.shaders import lit_with_shadows_shader

import random


class Enemy(Entity):
    def __init__(self, game, lane_x, z_position, car_type= 1):
        self.car_type = car_type
    
        if car_type == 1:   # fácil
            model = random.choice(os.listdir("app/assets/models/cars/easy"))
        elif car_type == 2: # normal
            model = random.choice(os.listdir("app/assets/models/cars/normal"))
        elif car_type == 3: # difícil
            model = random.choice(os.listdir("app/assets/models/cars/hard"))
        elif car_type == 4: # especial
            model = random.choice(os.listdir("app/assets/models/cars/special"))


        super().__init__(
            model=model,
            scale=(0.8, 0.4, 1.8),
            position=(lane_x, 0, z_position),
            shader=lit_with_shadows_shader 
        )

        self.speed = min(50, 10 * car_type)
        self.game = game
        self.lane_x = lane_x


    # ---------------------------------------------------------
    #   UPDATE DEL ENEMIGO (MOVIMIENTO + RECICLADO)
    # ---------------------------------------------------------
    def update(self):
        # mover hacia adelante
        self.z -= time.dt * self.speed

        # si pasa del jugador → destruir
        if self.z < self.game.player.z - 30:
            self.enabled = False

    # ---------------------------------------------------------
    #   RECICLAR ENEMIGO DELANTE
    # ---------------------------------------------------------
    def recycle(self):
        game = self.game

        recycle_z = game.player.z + game.enemy_spawn_distance

        # Banda cercana para evitar muros
        band = [e for e in game.enemies if abs(e.z - recycle_z) < 10 and e is not self]

        occupied = set(
            min(range(4), key=lambda i: abs(e.x - game.lanes[i]))
            for e in band
        )

        # Si hay hueco para reciclar
        if len(occupied) < 3:
            free = [i for i in range(4) if i not in occupied]
            if free:
                lane_index = random.choice(free)
                self.x = game.lanes[lane_index]
                self.z = recycle_z
                return

        # Si no se pudo reciclar → destruir
        if self.z < game.player.z - 200:
            destroy(self)
            game.enemies.remove(self)
