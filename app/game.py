# game.py
import random
from ursina import *
from ursina.shaders import lit_with_shadows_shader, unlit_shader

from entities import *
from managers import *
from config import *


class Game(Entity):
    def __init__(self):
        super().__init__()
        
        
        self.dashboard = Entity(parent= camera, model= "assets/models/cars/player/dashboard.glb",
                                 scale=(0.1, 0.13, 0.08), position=(0, -6, 1.4), shader=lit_with_shadows_shader)

        self.steerwheel = Entity(parent=camera, model="assets/models/cars/player/steerwheel.glb",
            scale=0.2, position=(-0.5, -1.2, 2), shader=lit_with_shadows_shader)

        self.collision_overlay = Entity(parent=camera.ui, model='quad', scale=(2,2), color=color.rgba32(255,0,0,0), shader= unlit_shader)

        # --- CARRILES ---
        self.lane_width = 2.8
        self.lanes = [-4.5 + i * self.lane_width for i in range(4)]
        
        # Entities
        self.player = Player() # ¡Managers use self.player!
        self.corona_power = CoronaPower(self, position=(0, 0.8, 0), scale= (0.12, 0.05, 0.12), rotation=(-12, 35, 0))

        # Config
        self.lives = Lives(game=self, heart_texture= "assets/textures/heart.png", max_lives=3)
        self.difficulty = Difficulty()
        self.day_cycle = DayCycle()
        self.music = MusicPlayer(folder_path="app/assets/sfx", volume=0.0)
        self.crash = Crash(self)
        

        # Managers
        self.road_manager = RoadManager(game=self, road_length=40, num_segments=15)
        self.power_manager = PowerManager(game=self)
        self.enemy_manager = EnemyManager(game=self)

        self.hitboxes = Hitboxes(player=self.player, enemies=self.enemy_manager.enemies, enabled=False)
        self.power_manager.add_power(self.corona_power)


        # --- CAMARA ---
        camera.parent = self.player
        camera.position = (0, 1.5, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90

       
    def start_crash_sequence(self):
        self.crash.active = True   
        
    # ---------------------------------------------------------
    #   UPDATE PRINCIPAL (ROBUSTO)
    # ---------------------------------------------------------
    def update(self):
        dt = time.dt

        if self.crash.active:
            self.crash.update(dt)
            return 

        # -------------------------
        # ACTUALIZAR CICLO DÍA / NOCHE
        # -------------------------
        sky_color, amb_color, sun_color, sun_angle = self.day_cycle.update()
        self.sky.color = sky_color
        self.ambient.color = amb_color
        self.sun.color = sun_color
        self.sun.look_at(Vec3(0, sun_angle, 1))


        # Rotación del volante
        steer_value = self.player.steering
        target_rotation = steer_value * 10
        self.steerwheel.rotation_z = lerp(self.steerwheel.rotation_z, target_rotation, dt * 5)

        self.difficulty.update(dt)
        self.music.update()


        self.player.update()
        self.player.speed = min(400, max(1, self.player.initial_speed * (self.difficulty.float_level / 2)))
        self.player.z += dt * self.player.speed

        self.power_manager.update()
        self.road_manager.update(self.player.z)
        self.enemy_manager.update(dt)

        # -------------------------
        # DETECTAR COLISIONES
        # -------------------------
        for enemy in self.enemy_manager.enemies:
            if distance(enemy.position, self.player.position) < self.hitboxes.enemy_hitbox_width / 2:
                self.collision_overlay.color = color.rgba32(255, 0, 0, 80)
                self.lives.lose_life()

        # -------------------------
        # ACTUALIZAR HITBOXES (SEGURA)
        # -------------------------
        if self.hitboxes and self.hitboxes.enabled:
            self.hitboxes.enemies = [e for e in self.enemy_manager.enemies if e.enabled]
            self.hitboxes.update()

        # -------------------------
        # AJUSTE DE SHADERS NOCHE/DÍA
        # -------------------------
        is_night = self.day_cycle.is_night()
        self.road_manager.set_night(is_night)
        for enemy in self.enemy_manager.enemies:
            enemy.shader = unlit_shader if is_night else lit_with_shadows_shader