class PowerManager:
    def __init__(self, game):
        self.game = game
        self.powers = []

    def add_power(self, power):
        self.powers.append(power)

    def update(self):
        for power in self.powers[:]:
            if not power.activated:
                power.z = self.game.player.z + 4
                power.x = self.game.player.x + 1.5
                power.try_activate()
            else:
                self.powers.remove(power)
