import random
import os

from ursina import *
from ursina.shaders import lit_with_shadows_shader, unlit_shader

class RoadManager:
    def __init__(self, game, road_length=40, num_segments=15, is_night=False):
        self.game = game
        self.road_length = road_length
        self.num_segments = num_segments
        self.is_night = is_night  # si es noche, se encienden las farolas

        self.road_segments = []
        self.terrain_left = []
        self.terrain_right = []
        self.grass_left = []
        self.grass_right = []
        self.sidewalks_left = []
        self.sidewalks_right = []
        self.props = []
        self.structures = []
        self.lamp_cones = []  # guardamos los conos de luz para mostrarlos solo de noche

        self.max_road_z = 0
        self.max_terrain_z = 0
        self.max_grass_z = 0
        self.max_sidewalk_z = 0
        self.max_props_z = 0
        self.max_structures_z = 0

        self.generate_initial_segments()

    def create_structures(self, base_z):
        buildings = os.listdir("app/assets/models/structures/buildings")
        hotels = os.listdir("app/assets/models/structures/hotels")
        houses = os.listdir("app/assets/models/structures/houses")

        rotation_y = 0

        for _ in range(5):
            category_name = random.choice(['buildings', 'hotels', 'houses'])
            if category_name in ['buildings', 'hotels']:
                category = buildings if category_name == 'buildings' else hotels
                position_x = 9
            else:
                category = houses
                position_x = 29

            chosen_model = random.choice(category)
            side_left = random.choice([True, False])
            if side_left:
                position_x *= -1
            else:
                rotation_y = 180

            overlap = any(abs(s.position.z - base_z) < 10 and abs(s.position.x - position_x) < 5 for s in self.structures)
            if not overlap:
                structure = Entity(
                    model=chosen_model,
                    scale=(3, 1, 5),
                    position=(position_x, 0, base_z),
                    rotation_y=rotation_y,
                    color=color.gray,
                    shader=lit_with_shadows_shader
                )
                self.structures.append(structure)
                self.max_structures_z = max(self.max_structures_z, base_z)
                break

    def generate_initial_segments(self):
        road_width = 18
        sidewalk_width = 4
        terrain_width = 1
        grass_width = 50
        props_models = os.listdir("app/assets/models/props")

        for i in range(self.num_segments):
            z_base = i * self.road_length

            # --- CARRETERA ---
            road = Entity(
                model='plane',
                texture="assets/textures/road.png",
                scale=(road_width, 0.1, self.road_length),
                position=(0, 0, z_base),
                shader=lit_with_shadows_shader,
                color=color.gray if not self.is_night else color.gray.tint(1.5)  # más brillante si es noche
            )
            self.road_segments.append(road)
            self.max_road_z = z_base

            # --- ACERAS ---
            sidewalk_pos_x = road_width / 2 + sidewalk_width / 2
            left_sidewalk = Entity(model='cube', color=color.gray, scale=(sidewalk_width, 0.1, self.road_length),
                                   position=(-sidewalk_pos_x, 0.05, z_base), shader=lit_with_shadows_shader)
            right_sidewalk = Entity(model='cube', color=color.gray, scale=(sidewalk_width, 0.1, self.road_length),
                                    position=(sidewalk_pos_x, 0.05, z_base), shader=lit_with_shadows_shader)
            self.sidewalks_left.append(left_sidewalk)
            self.sidewalks_right.append(right_sidewalk)
            self.max_sidewalk_z = z_base



            # --- HIERBA ---
            grass_pos_x = sidewalk_pos_x + sidewalk_width / 2 + grass_width / 2
            left_grass = Entity(model='cube', color='545e28', scale=(grass_width, 0.1, self.road_length),
                                position=(-grass_pos_x, 0.05, z_base), shader=lit_with_shadows_shader)
            right_grass = Entity(model='cube', color='545e28', scale=(grass_width, 0.1, self.road_length),
                                 position=(grass_pos_x, 0.05, z_base), shader=lit_with_shadows_shader)
            self.grass_left.append(left_grass)
            self.grass_right.append(right_grass)
            self.max_grass_z = z_base

            # --- PROPS ---
            props_positions = []
            for prop_model in props_models:
                for _ in range(5):
                    side = random.choice([1, -1])
                    z_offset = random.uniform(-self.road_length/2 + 2, self.road_length/2 - 2)
                    x_pos = 8 * side
                    z_pos = z_base + z_offset

                    if any(abs(px - x_pos) < 2 and abs(pz - z_pos) < 4 for px, pz in props_positions):
                        continue

                    prop = Entity(model=prop_model, scale_y=0.5, position=(x_pos, 0, z_pos),
                                  shader=lit_with_shadows_shader, rotation_y=0 if side == 1 else 180)
                    self.props.append(prop)
                    props_positions.append((x_pos, z_pos))
                    self.max_props_z = max(self.max_props_z, z_pos)

                    # farola
                    if os.path.splitext(prop_model)[0].lower() == "street_lamp":
                        cone = Entity(parent=prop, model=Cone(resolution=10), scale=(1, 8, 1),
                                      position=(-1.85, 3.8, 0), rotation=(0, 0, 0),
                                      color=color.rgba32(255, 255, 200, 30))
                        cone.enabled = self.is_night  # solo mostrar cono de luz si es noche
                        self.lamp_cones.append(cone)
                    break

            # crear estructuras
            self.create_structures(z_base + random.uniform(-7, 7))


    def set_night(self, is_night: bool):
        self.is_night = is_night
        for road in self.road_segments:
            if self.is_night:
                road.shader = unlit_shader
            else:
                road.shader = lit_with_shadows_shader  # vuelve al shader normal
        for cone in self.lamp_cones:
            cone.enabled = self.is_night

    def recycle_segments(self, segments, player_z):
        # calcular max z de todos los segmentos actualmente visibles
        max_z = max(seg.z for seg in segments)
        for seg in segments:
            if seg.z + self.road_length < player_z - 5:
                seg.z = max_z + self.road_length
                max_z = seg.z  # actualizar para el siguiente segmento


    def recycle_terrain(self, terrains, player_z):
        max_z = max(t.z for t in terrains)
        for t in terrains:
            # si el terrain está lo suficientemente atrás
            if t.z + 5 * self.road_length < player_z - 5:
                t.z = max_z + 5 * self.road_length
                max_z = t.z



    def update(self, player_z):
        self.recycle_segments(self.road_segments, player_z)
        self.recycle_segments(self.grass_left, player_z,)
        self.recycle_segments(self.grass_right, player_z)
        self.recycle_segments(self.sidewalks_left, player_z)
        self.recycle_segments(self.sidewalks_right, player_z)

        for obj_list, max_attr in [(self.props, 'max_props_z'), (self.structures, 'max_structures_z')]:
            for obj in obj_list:
                if obj.z < player_z - 5:
                    max_z = getattr(self, max_attr)
                    obj.z = max_z + self.road_length
                    setattr(self, max_attr, obj.z)
