# game.py
import random
from ursina import *
from ursina.shaders import lit_with_shadows_shader, unlit_shader

from entities.player import Player
from entities.enemy import Enemy
from entities.road_manager import RoadManager
from config.day_cycle import DayCycle
from config.difficulty import Difficulty
from entities.power.corona_power import CoronaPower
from config.hitboxes import Hitboxes

class Game(Entity):
    def __init__(self):
        super().__init__()
        
        # --- SPRITE DEL SALPICADERO / VOLANTE ---
        self.dashboard = Entity(     
            parent= camera,    
            model= "assets/models/cars/player/dashboard.glb",
            scale=(0.1, 0.13, 0.08),      
            position=(0, -6, 1.4),   # -2 #0.9      
            rotation=(0,0,0),
            shader=lit_with_shadows_shader
        )

        # --- SPRITE DEL VOLANTE ---
        self.steerwheel = Entity(
            parent=camera,
            model="assets/models/cars/player/steerwheel.glb",
            scale=0.2,                  
            position=(-0.5, -1.2, 2),  
            shader=lit_with_shadows_shader          
        )

        # Overlay rojo full screen
        self.collision_overlay = Entity(
            parent=camera.ui,  # siempre sobre la cámara
            model='quad',
            scale=(2,2),      # cubre toda la pantalla
            color=color.rgba32(255,0,0,0),  # transparente al inicio
            shader= unlit_shader
        )


        # --- CARRILES ---
        self.lane_width = 2.8
        self.lanes = [-4.5 + i * self.lane_width for i in range(4)]

        # --- ROAD MANAGER ---
        self.road = RoadManager(
            game=self,
            road_length=40,
            num_segments=15
        )

        # --- ENEMIGOS ---
        self.enemies = []
        self.enemy_speed = 15
        self.enemy_spawn_distance = 200
        self.max_enemies = 8

        # --- GENERACIÓN ---
        self.spawn_timer = 0
        self.spawn_interval = 2
        self.spawn_acceleration = 0.995

        # --- JUGADOR ---
        self.player = Player()

        # --- POWERUPS ---
        self.powers = []

        # Creamos una botella flotante en un carril aleatorio
        self.corona_power = CoronaPower(self, position=(0, 0.8, 0), scale= (0.12, 0.05, 0.12), rotation=(-12, 35, 0))
        self.powers.append(self.corona_power)


        ### --- DAY CYCLE ---
        self.day_cycle = DayCycle()

        ### --- DIFFICULTY ---
        self.difficulty = Difficulty()

        # --- CAMARA ---
        camera.parent = self.player
        camera.position = (0, 1.5, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90

        # Velocidad del coche
        self.speed = 100

        self.hitboxes = Hitboxes(player=self.player, enemies=self.enemies, enabled=False)

    

    # ---------------------------------------------------------
    #   SPAWN ENEMIGOS
    # ---------------------------------------------------------
    def spawn_enemy(self):
        if len(self.enemies) >= self.difficulty.max_enemies:
            return

        base_z = self.player.z + self.enemy_spawn_distance

        for _ in range(10):
            z_position = base_z + random.uniform(0, 80)
            if any(abs(e.z - z_position) < 20 for e in self.enemies):
                continue

            band = [e for e in self.enemies if abs(e.z - z_position) < 10]
            occupied = set(min(range(4), key=lambda i: abs(e.x - self.lanes[i])) for e in band)
            if len(occupied) >= 3:
                continue

            free = [i for i in range(4) if i not in occupied]
            if not free:
                continue

            lane = random.choice(free)
            lane_x = self.lanes[lane]

            # Elegir tipo de coche según dificultad
            car_type = self.difficulty.choose_car_type()

            # Crear enemigo con tipo
            enemy = Enemy(self, lane_x, z_position, car_type=car_type)
            self.enemies.append(enemy)

            if self.hitboxes.enabled:
                self.hitboxes.add_enemy(enemy)
    
            return


    # ---------------------------------------------------------
    #   ACTUALIZA MAPA + ENEMIGOS (SEGURA)
    # ---------------------------------------------------------
    def update_road(self):
        """Actualiza carretera y enemigos de forma segura, sin modificar la lista durante la iteración."""
        # Actualizar segmentos de carretera
        self.road.update(self.player.z)

        # Actualizar enemigos existentes
        to_destroy = []
        for enemy in self.enemies[:]:  # [:] = copia segura
            if enemy.enabled:
                enemy.update()
            else:
                to_destroy.append(enemy)

        # Eliminar enemigos destruidos
        for enemy in to_destroy:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
                destroy(enemy)

        # Detectar colisiones simples (feedback visual)
        for enemy in self.enemies:
            if distance(enemy.position, self.player.position) < self.hitboxes.enemy_hitbox_width / 2:
                self.collision_overlay.color = color.rgba32(255, 0, 0, 80)



    # ---------------------------------------------------------
    #   UPDATE PRINCIPAL (ROBUSTO)
    # ---------------------------------------------------------
    def update(self):
        dt = time.dt

        # -------------------------
        # 1️⃣ LIMPIEZA INICIAL
        # -------------------------
        # Eliminar enemigos destruidos antes de cualquier otro cálculo
        self.enemies = [e for e in self.enemies if e.enabled]
        self.collision_overlay.color = lerp(self.collision_overlay.color, color.rgba32(255, 0, 0, 0), dt * 5)

        # -------------------------
        # 2️⃣ ACTUALIZAR CICLO DÍA / NOCHE
        # -------------------------
        sky_color, amb_color, sun_color, sun_angle = self.day_cycle.update()
        self.sky.color = sky_color
        self.ambient.color = amb_color
        self.sun.color = sun_color
        self.sun.look_at(Vec3(0, sun_angle, 1))

        # -------------------------
        # 3️⃣ DIFICULTAD
        # -------------------------
        self.difficulty.update(dt)

        # Suavizar el cambio de cantidad máxima de enemigos
        target_max = self.difficulty.max_enemies
        self.max_enemies = int(lerp(self.max_enemies, target_max, dt * 2))

        # -------------------------
        # 4️⃣ ACTUALIZAR JUGADOR
        # -------------------------
        self.player.update()
        self.player.z += dt * self.speed

        # Rotación del volante
        steer_value = self.player.steering
        target_rotation = steer_value * 10
        self.steerwheel.rotation_z = lerp(self.steerwheel.rotation_z, target_rotation, dt * 5)

        # -------------------------
        # 5️⃣ ACTUALIZAR PODERES
        # -------------------------
        for power in self.powers[:]:
            if not power.activated:
                power.z = self.player.z + 4
                power.x = self.player.x + 1.5
                power.try_activate()
            else:
                self.powers.remove(power)

        # -------------------------
        # 6️⃣ ACTUALIZAR CARRETERA + ENEMIGOS
        # -------------------------
        self.update_road()

        # -------------------------
        # 7️⃣ ACTUALIZAR HITBOXES (SEGURA)
        # -------------------------
        if self.hitboxes and self.hitboxes.enabled:
            self.hitboxes.enemies = [e for e in self.enemies if e.enabled]
            self.hitboxes.update()

        # -------------------------
        # 8️⃣ GENERAR NUEVOS ENEMIGOS
        # -------------------------
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = self.difficulty.spawn_interval

        while len(self.enemies) < self.max_enemies:
            self.spawn_enemy()

        # -------------------------
        # 9️⃣ AJUSTE DE SHADERS NOCHE/DÍA
        # -------------------------
        is_night = self.day_cycle.is_night()
        self.road.set_night(is_night)
        for enemy in self.enemies:
            enemy.shader = unlit_shader if is_night else lit_with_shadows_shader
