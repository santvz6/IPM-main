import random


class Difficulty:
    def __init__(self):
        self.time_elapsed = 0.0
        self.level = 1

        # parámetros base
        self.spawn_interval = 2.0
        self.max_enemies = 5
        self._max_enemies = 6

        # tipos de coche: 1=fácil, 2=normal, 3=difícil, 4=especial
        self.car_types = {
            1: 0.7,  # fácil
            2: 0.2,  # normal
            3: 0.08, # difícil
            4: 0.02  # especial
        }

    def update(self, dt):
        self.time_elapsed += dt
        self.level = 1 + int(self.time_elapsed // 1)
        print("level: ", self.level)

        # ajustamos spawn_interval y velocidad según el nivel
        self.spawn_interval = max(0.5, 2.0 * (0.95 ** self.level))
        self.max_enemies = min(self._max_enemies, 3 * self.level)

        # ajustamos probabilidades de coches según el nivel
        # ejemplo: a mayor nivel, aumenta la probabilidad de coches difíciles y especiales
        easy_prob = max(0.3, 0.7 - 0.05 * self.level)
        normal_prob = min(0.4, 0.2 + 0.02 * self.level)
        hard_prob = min(0.25, 0.08 + 0.02 * self.level)
        special_prob = 1.0 - (easy_prob + normal_prob + hard_prob)

        self.car_types = {
            1: easy_prob,
            2: normal_prob,
            3: hard_prob,
            4: special_prob
        }

    def choose_car_type(self):
        r = random.random()
        acc = 0
        for car_type, prob in self.car_types.items():
            acc += prob
            if r <= acc:
                return car_type
        return 1  # fallback
