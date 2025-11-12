# player.py

import socket
from ursina import *

class Player(Entity):
    def __init__(self):
        super().__init__(model='cube', color=color.red, scale=(1,0.5,2))
        
        # socket cliente
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 5005))
        self.sock.setblocking(False)

        # steering actual
        self.steering = 0

    def update(self):
        # Leer steering del servidor mediapipe
        try:
            data, addr = self.sock.recvfrom(1024)
            self.steering = float(data.decode())
        except BlockingIOError:
            pass

      
        if held_keys['a']:
            self.steering = -6
        if held_keys['d']:
            self.steering = 6
        if held_keys["h"]:
            self.steering = 9999

        if self.steering != 9999 and self.steering != 8888:
            self.x += self.steering * time.dt * 0.7


        # límites
        self.x = clamp(self.x, -5, 5)
