# current timestamp
# board state

# a 2d array that stores either players or walls

class Game:
    def __init__(self, _size):
        self.game_grid = [[0 for i in range(_size)] for j in range(_size)]
        self.started = False
        self._size = _size

    def spawn_player(self, player):
        a = 1

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def reset_game(self):
        self.game_grid = [[0 for i in range(self._size)] for j in range(self._size)]
        self.started = False