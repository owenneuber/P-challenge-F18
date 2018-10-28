# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 10:25:46 2018

@author: Owen
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey , DateTime, Boolean#, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import HSTORE, JSON
from sqlalchemy.orm import relationship, backref, sessionmaker


Base  = declarative_base()

engine = create_engine('postgresql://postgres:q1w2e3@localhost/WEC.db')
"""
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session (for local testing)
session = Session()
"""
class Game_state(Base): # Keeps track of all current and (if we want) past gamestates of all games
    __tablename__ = 'Game_state'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('Games.id'), nullable=False) #The ID of the game this gamestate corresponds to
    turn = Column(Integer, nullable=False) #tells you the turn the current gamestate corresponds to
    game_state = Column(JSON)
    time_stamp = Column(DateTime)
    games = relationship('Games', backref=backref('Game_state', lazy='dynamic', cascade='all,delete'))
    
    def __repr__(self):
        return '<Game_state(id: {id}, game_id: {game_id}, turn: {turn}, time_stamp: {time_stamp})>'.format(
            id=self.id,
            game_id=self.game_id,
            turn=self.turn,
            time_stamp=self.time_stamp)
            
        
class Games(Base): # Keep track of our matches as an overview: who is playing who, is it done, who won?
    __tablename__ = 'Games'
    
    id = Column(Integer, primary_key=True)    
    team1_id = Column(Integer)
    team2_id = Column(Integer)
    is_complete = Column(Boolean, default=False) # has the game finished or not?
    victor = Column(String, default=None) # the winning team's ID should go in this column
    
    def __repr__(self): #returns the name of the contig, it's length, and its genome of origin
        return '<Games(game number: {0}, team 1 ID: {1}, team 2 ID: {2}, game completed: {3}, victor: {4})>'.format(
                self.id, 
                self.team1_id, 
                self.team2_id, 
                self.is_complete, 
                self.victor)


class Teams(Base): # Keeps track of all the teams and their stats
    __tablename__ = 'Teams'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, index=True, nullable=False)
    team_key = Column(String, nullable=False) # the secret password which teams use to validate their requests
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)

    def __repr__(self):
        return  '<Teams(team ID: {0}, team key: {1}, games played: {2}, game won: {3})>'.format(
                self.team_id, 
                self.team_key, 
                self.games_played, 
                self.games_won)

Base.metadata.create_all(engine) #you need to execute this everytime you make a new table