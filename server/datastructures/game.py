# current timestamp
# board state

# a 2d array that stores either players or walls
from .models import Games, Game_state, Teams
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
        
        ############## creat DB session and add game to it
        engine = engine = create_engine('postgresql://postgres:q1w2e3@localhost/WEC.db') 
        Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
        self.session = Session()
        try:
            self.current_game = Games(team1_id=None,team2_id=None)
            self.session.add(self.current_game)
            self.session.commit()
            self.game_state = Game_state(game_id=self.current_game.id, turn=0, game_state=self.game_grid)
            self.session.add(self.game_state)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(e)
        #################
        

    def spawn_player(self, team_id):
        row = int(self._size/2)
        col = int(self._size/4)
        position = 1
        if self.game_grid[str(row)+","+str(col)] != "": #if the first player has already been put in
            col *= 3
            position = 2
        self.game_grid.update({str(row)+","+str(col):team_id})
        ##################
        try:
            if position == 1:
                self.current_game.team1_id = team_id
            else:
                self.current_game.team2_id = team_id
            self.game_state.game_state = self.game_grid
            self.session.add(self.current_game)
            self.session.add(self.game_state)
        except Exception as e:
            self.session.rollback()
            print(e)
        ###################
        

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def reset_game(self):
        self.game_grid = self.build_grid(_size)
        self.started = False
        
    def update_game_state(self, update):
        """ Updates the game_grid with the imputed update variable. update should
        be a dictionary containing as many updates as desired (separated by commans) in the format:
        {"i,j":val, "1,2":"P2", ...} where i and j are the row and column position to be updated
        and val is the new string value to give that position. """
        self.game_grid.update(update)
        ##################
        try:
            self.game_state.game_state = self.game_grid
            self.game_state.turn += 1
            self.game_state.game_state
            self.session.add(self.game_state)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(e)
        ##################