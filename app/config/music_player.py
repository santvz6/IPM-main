# music_player.py
import os
import pygame
import random
from ursina import held_keys


class MusicPlayer:
    def __init__(self, folder_path, volume=0.5):
        self.folder_path = folder_path
        self.volume = max(0, min(1, volume))

        # Inicializamos pygame mixer
        pygame.mixer.init()
        
        # Cargamos solo archivos compatibles (.wav, .ogg, .mp3)
        self.songs = [f for f in os.listdir(self.folder_path)
                      if f.endswith((".wav", ".ogg", ".mp3"))]
        random.shuffle(self.songs)
        
        if not self.songs:
            print("No se encontraron canciones válidas en", folder_path)
            self.current_index = -1
            return

        self.current_index = 0
        self._load_current_audio()

    # ---------------------------------------------------------
    #   Funciones de control
    # ---------------------------------------------------------
    def _load_current_audio(self):
        """Carga la canción actual y reproducir en loop infinito"""
        song_path = os.path.join(self.folder_path, self.songs[self.current_index])
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)  # -1 = loop infinito

    def play(self):
        pygame.mixer.music.unpause()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def stop(self):
        pygame.mixer.music.stop()

    def next(self):
        if not self.songs:
            return
        self.current_index = (self.current_index + 1) % len(self.songs)
        self._load_current_audio()

    def previous(self):
        if not self.songs:
            return
        self.current_index = (self.current_index - 1) % len(self.songs)
        self._load_current_audio()

    def set_volume(self, volume):
        self.volume = max(0, min(1, volume))
        pygame.mixer.music.set_volume(self.volume)

    def increase_volume(self, step=0.05):
        self.set_volume(self.volume + step)

    def decrease_volume(self, step=0.05):
        self.set_volume(self.volume - step)


    def update(self):
        # Control de volumen con teclado
        if held_keys["+"]:
            self.increase_volume(0.01)
        if held_keys["-"]:
            self.decrease_volume(0.01)
