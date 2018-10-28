# current timestamp
# board state

# a 2d array that stores either players or walls

class Game:
    def build_grid(self, _size): 
        """ Build a dictionary grid. The key will be a position string (e.g. "1,1")
        the value will be what is occupying the space (options for that are:
        'wall', player_id1, player_id2, 'trail, and '' (for nothing)."""
        _size += 2 # to allow for walls to be added on the periphery
        game_grid = {}
        for i in range(_size):
            for j in range(_size):
                val = ""
                if i == 0 or j == 0 or i == _size-1 or j == _size-1:
                    val = "wall"
                game_grid.update({str(i)+","+str(j):val})                
        return game_grid
    
    def __init__(self, _size):
        self.game_grid = self.build_grid(_size)
        self.started = False
        self._size = _size

    def spawn_player(self, _size, player):
        row = int(_size/2)
        col = int(_size/4)
        if self.game_grid[(row,col)] != "": #if the first player has already been put in
            col *= 3
        self.game_grid.update({(row,col):player})

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def reset_game(self):
        self.game_grid = self.build_grid(_size)
        self.started = False