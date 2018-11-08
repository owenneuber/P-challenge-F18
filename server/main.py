#!/usr/bin/env python3

import asyncio
import sys
from json import JSONDecodeError

import aiohttp
from aiohttp import web
import logging
import json
from datastructures.models import Teams
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datastructures.game import Game

from datastructures.move_queue import MoveQueue

GAME_LOOP_INTERVAL_IN_SECONDS = 3
GAME_GRID_SIZE = 10

logging.basicConfig(level=logging.INFO)
game = Game(GAME_GRID_SIZE)

engine = create_engine('postgresql://postgres:q1w2e3@localhost/WEC.db')
Session = sessionmaker(bind=engine)
session = Session() # session to use in functions which need it

def validate_team(team_id, token):
    """ Returns True if the team is who they claim to be, False if not. """
    global session
    team = session.query(Teams).filter_by(team_id=team_id).first()
    if team == None: # i.e. the provided team id does not exist in the db
        return False
    return team.team_key == token

# HTTP endpoint to start game (i.e. sets game_started as true)
async def start_game(request):
    global game
    if game.started == False and len(move_queue_dict) == 2:
        game.start()
        logging.info("Starting game")
        data = {"Result" : "Game started"}
    else:
        data = {"Result" : "Game not started."}
    return web.json_response(data)

async def stop_game(request):
    global game
    if game.started == True:
        game.stop()
        logging.info("Stopping game")
        data = {"Result" : "Game stopped"}
        # TODO: reset everything - close conns, reset game state, etc.
    else:
        data = {"Result" : "Game not stopped.  Game is not running."}
    return web.json_response(data)

# one handler spawned per websocket /connect request
async def wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app["sockets"].append(ws)

    # If game is in progress, close connection (do not accept new conns)
    if game.started == True:
        await ws.send_str("Game in progress, connection rejected")
        app["sockets"].remove(ws)
        logging.info("Closing connection since game is already in progress")
        return ws

    while 1:
        msg = await ws.receive()
        if msg.type == aiohttp.WSMsgType.TEXT:
            logging.info("Received message %s" % msg.data)
            deserialized_data = json.loads(msg.data)
            if not validate_team(deserialized_data["team_id"], deserialized_data["authenticationKey"]): # check if team is who they say they are
                logging.info("Team id and/or token invalid")
                await ws.send_str("The team id and/or token you provided is invalid.")
                break
            logging.info("Team number %s validated" % deserialized_data["team_id"])
            try:
                handle_request(deserialized_data)
                await ws.send_str("Echo: {}".format(msg.data))
            except ValueError as e:
                await ws.send_str("Invalid input.  Reason: " + e.args[0])

        elif msg.type == aiohttp.WSMsgType.CLOSE or\
            msg.type == aiohttp.WSMsgType.ERROR:
                break
    app["sockets"].remove(ws)
    logging.info("Closed connection.")
    return ws

async def dev_wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app["dev_sockets"].append(ws)

    while 1:
        msg = await ws.receive()
        if msg.type == aiohttp.WSMsgType.TEXT:
            logging.info("Received message %s" % msg.data)
        elif msg.type == aiohttp.WSMsgType.CLOSE or\
            msg.type == aiohttp.WSMsgType.ERROR:
                break

        if is_valid_message(msg.data):
            await ws.send_str("Valid message.  %s" % msg.data)
        else:
            await ws.send_str("Invalid message.  %s" % msg.data)

    app["sockets"].remove(ws)
    logging.info("Closed connection.")
    return ws

def move_from_to(team_id, move_direction):
    """Takes in the message of a user who is moving and returns the grid position
    they started in and the one they intend to move to (in a tuple). """
    global game
    original_position = list(game.game_grid.keys())[list(game.game_grid.values()).index(team_id)] # "row,column"
    new_position = list(map(int, original_position.split(","))) # [int(row), int(column)]
    if move_direction == "UP":
        new_position[0] -= 1
    elif move_direction == "DOWN":
        new_position[0] += 1
    elif move_direction == "RIGHT":
        new_position[1] += 1
    elif move_direction == "LEFT":
        new_position[1] -= 1
    return (original_position, str(new_position[0]) +","+ str(new_position[1])) # return ("row1,column1", "row2,column2")

def handle_request(messageDict):
    global game
    global session
    if "type" in messageDict and "message" in messageDict and "team_id" in messageDict and "authenticationKey" in messageDict:
        if messageDict["type"].upper() == "REGISTRATION":
            if int(messageDict["team_id"]) not in move_queue_dict:
                game.spawn_player(int(messageDict["team_id"]))
                move_queue_dict[messageDict["team_id"]] = MoveQueue(int(messageDict["team_id"]))
            else:
                raise ValueError("Player already registered")
        elif messageDict["type"].upper() == "MOVE":
            if messageDict["team_id"] not in move_queue_dict:
                logging.info("Unregistered team tried to submit a move.")
                raise ValueError("Unregistered team " + messageDict["team_id"] + " tried to submit a move.")
            elif messageDict["message"].upper() not in ("UP", "DOWN", "LEFT", "RIGHT"):
                logging.info("Invalid move %s received " % messageDict["message"])
                raise ValueError("Invalid move " + messageDict["message"] + " received.")
            else:
                logging.info("Received move %s from team %s." % (messageDict["message"], messageDict["team_id"]))
                move_queue_dict[messageDict["team_id"]].add_move(messageDict["message"].upper())
        else:
            logging.info("Message with invalid type received: " + json.dumps(messageDict))
            raise ValueError("Message with invalid type " + messageDict["type"] + " received.")
    else:
        logging.info("Message with missing field received: " + json.dumps(messageDict))
        raise ValueError("Message with missing field received.")
    return

def get_json_serialized_game_state():
    global game
    if game.current_game.is_complete == True:
        return ("Game Complete: Team " + str(game.current_game.victor) + " won the match")
    return json.dumps(game.game_grid)

# This game loop will run infinitely and will periodically send back a JSON string summarizing game state if game is
# active
async def game_loop(app):
    global game
    global session
    while 1:
        if game.started:
            apply_moves()
            print_game_state()
            for ws in app["sockets"]:
                await ws.send_str(get_json_serialized_game_state())
            #if game.current_game.is_complete:
            #    game.stop() Not sure if this should be here
            # If the game is done, should we exit out of this loop? idk
        await asyncio.sleep(GAME_LOOP_INTERVAL_IN_SECONDS)

def print_game_state():
    global game
    game_state_dict = game.game_grid
    game_arr = []
    for i in range(0, 12):
        new = []
        for j in range(0, 12):
            new.append("")
        game_arr.append(new)

    for key in game_state_dict:
        pair = key.split(",")
        row = int(pair[0])
        col = int(pair[1])
        game_arr[row][col] = (game_state_dict[key])

    for i in range(0, 12):
        for j in range(0, 12):
            val = game_arr[i][j]
            if val == "":
                sys.stdout.write("0")
            elif val == "wall":
                sys.stdout.write("W")
            elif val == "trail":
                sys.stdout.write("T")
            elif val == "collision":
                sys.stdout.write("C")
            elif "_dead" in str(val):
                sys.stdout.write(val.rstrip("_dead")+"D")
            else:
                sys.stdout.write(str(val))
        print("")

def apply_moves():
    team1, team2 = move_queue_dict.items() # 2 tuples of form: (team_id, MoveQueue object)
    start1, moving_to1 = move_from_to(team1[0], team1[1].dequeue_oldest_move().upper())
    start2, moving_to2 = move_from_to(team2[0], team2[1].dequeue_oldest_move().upper())
    team1_dead = False
    team2_dead = False
    collision = False
    logging.info("team " +str(team1[0]) + ": " + start1 + " --> " + moving_to1)
    logging.info("team " +str(team2[0]) + ": " + start2 + " --> " + moving_to2)
    
    if moving_to1 == moving_to2: # they collided!
        team1_dead = True
        team2_dead = True
        collision = True
        game.current_game.victor = None
        logging.info("Both player collided")
        game.update_game_state({start1: "trail", start2: "trail", moving_to1: "collision"})
    else:
        if game.game_grid[moving_to1] != "":
            team1_dead = True
            
        if game.game_grid[moving_to2] != "":
            team2_dead = True
        
    if (not team1_dead) and (not team2_dead): # neither player died so move the player as requested and set their old position as "trail"
        game.update_game_state({start1: "trail", start2: "trail", moving_to1: team1[0], moving_to2: team2[0]})
        return # the rest of the function can be skipped if both players lived

    if team1_dead and team2_dead and not collision:
        game.current_game.victor = None
        logging.info("Both player died at the same time. Neither team wins.")
        game.update_game_state({start1: "trail", start2: "trail", moving_to1: str(team1[0])+"_dead", moving_to2: str(team2[0])+"_dead"})
    elif team1_dead:
        game.current_game.victor = int(team2[0])
        game.update_game_state({start1: "trail", start2: "trail", moving_to1: str(team1[0])+"_dead", moving_to2: team2[0]})
    elif team2_dead:
        game.current_game.victor = int(team1[0])
        game.update_game_state({start1: "trail", start2: "trail", moving_to1: team1[0], moving_to2: str(team2[0])+"_dead"})
        
    if game.current_game.victor:
        logging.info("Team " + str(game.current_game.victor) + " won the match")
            
    game.current_game.is_complete = True
    game.finish(game.current_game.victor)

def is_valid_message(serialized_message):
    try:
        deserialized_data = json.loads(serialized_message)
        if ("type" not in deserialized_data or "message" not in deserialized_data \
                or "authenticationKey" not in deserialized_data or "team_id" not in deserialized_data) and len(deserialized_data) == 2:
            return False
        if deserialized_data["type"].upper() == "MOVE" and deserialized_data["message"].upper() not in ("LEFT","RIGHT","UP","DOWN"):
            return False
    except JSONDecodeError:
        return False
    return True

app = web.Application()

# a list of all the active socket connections
app["sockets"] = []

app["dev_sockets"] = []

# a dictionary of id - move queue pairs
move_queue_dict = {}

asyncio.ensure_future(game_loop(app))

app.router.add_route("GET", "/connect", wshandler)
app.router.add_route("GET", "/connect_dev", dev_wshandler)
app.router.add_route("GET", "/startGame", start_game)
app.router.add_route("GET", "/stopGame", stop_game)


web.run_app(app)