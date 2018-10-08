# current timestamp
# board state

# a 2d array that stores either players or walls

class Game:
    def __init__(self, _size):
        self.game_grid = [[0 for i in range(_size)] for j in range(_size)]