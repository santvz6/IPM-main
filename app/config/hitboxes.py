from ursina import *
from ursina.shaders import unlit_shader

class Hitboxes(Entity):
    def __init__(self, player, enemies, enabled=True):
        super().__init__()
        self.player = player
        self.enemies = enemies
        self.enabled = enabled

        self.enemy_hitbox_width = 4

        # Hitbox del jugador
        self.player_hitbox_length = 20
        self.player_line = Entity(
            parent=scene,
            model='cube',
            color=color.red,
            scale=(0.05, 0.05, self.player_hitbox_length),  
            position=self.player.position,
            shader=unlit_shader,
            alpha=0.7,
            render_queue=2
        )

        self.enemy_boxes = []


    def add_enemy(self, enemy):
        self.enemies.append(enemy)


    def update(self):
        if not self.enabled:
            return

        # Actualizar línea del jugador
        self.player_line.position = self.player.position + Vec3(0, 0, self.player_hitbox_length/2)


        # Crear nuevas cajas para enemigos que aparecieron
        while len(self.enemy_boxes) < len(self.enemies):
            e = self.enemies[len(self.enemy_boxes)]
            box = Entity(
                model='cube',
                color=color.orange,
                scale= e.scale * 4,
                position=e.position,
                rotation=e.rotation,
                shader=unlit_shader,
                alpha=0.7
            )
            box.scale_x = self.enemy_hitbox_width * 0.9
            self.enemy_boxes.append(box)

        # Actualizar posiciones y eliminar los que ya no existen
        for i in reversed(range(len(self.enemy_boxes))):
            if i >= len(self.enemies):
                destroy(self.enemy_boxes[i])
                self.enemy_boxes.pop(i)
            else:
                e = self.enemies[i]
                box = self.enemy_boxes[i]
                box.position = e.position
                box.rotation = e.rotation
        
