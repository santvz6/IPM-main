from ursina import destroy
from entities.enemy import Enemy
import random

class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemies = []
        self.spawn_timer = 0

    def update(self, dt):
        # Actualizar enemigos existentes
        to_destroy = []
        for enemy in self.enemies[:]:
            if enemy.enabled:
                enemy.update()
            else:
                to_destroy.append(enemy)

        for enemy in to_destroy:
            self.enemies.remove(enemy)
            destroy(enemy)

        # Detectar colisiones simples
        for enemy in self.enemies:
            if (self.game.player.position - enemy.position).length() < self.game.hitboxes.enemy_hitbox_width / 2:
                self.game.collision_overlay.color = color.rgba32(255, 0, 0, 80)

        # Spawn de enemigos
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = self.game.difficulty.spawn_interval

        while len(self.enemies) < self.game.max_enemies:
            self.spawn_enemy()

    def spawn_enemy(self):
        if len(self.enemies) >= self.game.difficulty.max_enemies:
            return

        base_z = self.game.player.z + self.game.enemy_spawn_distance
        for _ in range(10):
            z_position = base_z + random.uniform(0, 80)
            if any(abs(e.z - z_position) < 20 for e in self.enemies):
                continue

            band = [e for e in self.enemies if abs(e.z - z_position) < 10]
            occupied = set(min(range(4), key=lambda i: abs(e.x - self.game.lanes[i])) for e in band)
            if len(occupied) >= 3:
                continue

            free = [i for i in range(4) if i not in occupied]
            if not free:
                continue

            lane = random.choice(free)
            lane_x = self.game.lanes[lane]

            car_type = self.game.difficulty.choose_car_type()
            enemy = Enemy(self.game, lane_x, z_position, car_type=car_type)
            self.enemies.append(enemy)

            if self.game.hitboxes.enabled:
                self.game.hitboxes.add_enemy(enemy)

            return
