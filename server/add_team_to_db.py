# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 16:03:22 2018

@author: Owen
"""

import secrets
from datastructures.models import Teams
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



team_number = int(input("What is the team's number? "))

token = secrets.token_hex(20)

try:
    engine = engine = create_engine('postgresql://postgres:q1w2e3@localhost/WEC.db') 
    Session = sessionmaker(bind=engine)
    session = Session()
    
    new_team = Teams(team_id=team_number, team_key=token)
    session.add(new_team)
    session.commit()
    print("Team number " + str(team_number) + " has token: ")
    print(token)
except:
    session.rollback()
finally:
    session.close()