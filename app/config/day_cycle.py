from ursina import *

class DayCycle:
    def __init__(self, day_speed=0.02, phase_percentages=None):
        self.day_time = 0.0
        self.day_speed = day_speed

        # Fases por defecto
        if phase_percentages is None:
            phase_percentages = {
                "sunset": 0.1,
                "night": 0.5,
                "sunrise": 0.1,
                "day": 0.3
            }

        self.phases = list(phase_percentages.keys())
        self.phase_durations = list(phase_percentages.values())
        # generar acumulado para comparar fácilmente
        self.phase_accum = []
        acc = 0
        for d in self.phase_durations:
            acc += d
            self.phase_accum.append(acc)

        # Colores por fase
        self.sky_colors = [
            color.rgb32(180, 100, 80),   # sunset
            color.rgb32(10, 20, 40),     # night
            color.rgb32(200, 150, 120),  # sunrise
            color.rgb32(120, 180, 220)   # day
        ]
        self.amb_colors = [
            color.rgb32(50, 30, 25),
            color.rgb32(3, 3, 8),
            color.rgb32(80, 50, 40),
            color.rgb32(200, 200, 220)
        ]
        self.sun_colors = [
            color.rgb32(200, 140, 90),
            color.rgb32(15, 15, 35),
            color.rgb32(220, 180, 100),
            color.rgb32(255, 255, 230)
        ]

    def update(self):
        self.day_time += time.dt * self.day_speed
        if self.day_time > 1:
            self.day_time -= 1

        t = self.day_time

        # determinar fase actual y siguiente según phase_accum
        for i, end in enumerate(self.phase_accum):
            if t < end:
                phase_index = i
                next_index = (i + 1) % len(self.phases)
                start = 0 if i == 0 else self.phase_accum[i-1]
                local_t = (t - start) / (end - start)
                break

        # interpolación de colores
        sky_color = lerp(self.sky_colors[phase_index], self.sky_colors[next_index], local_t)
        amb_color = lerp(self.amb_colors[phase_index], self.amb_colors[next_index], local_t)
        sun_color = lerp(self.sun_colors[phase_index], self.sun_colors[next_index], local_t)

        sun_angle = lerp(-0.3, -1.0, t)  # movimient del sol

        return sky_color, amb_color, sun_color, sun_angle

    def is_night(self):
        t = self.day_time
        return 0.05 < t < 0.3
