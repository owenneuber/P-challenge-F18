#!/usr/bin/env python3

import asyncio
import sys

import aiohttp
from aiohttp import web
import logging
import json
from datastructures.models import Teams
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datastructures.game import Game

from server.datastructures.move_queue import MoveQueue

GAME_LOOP_INTERVAL_IN_SECONDS = 3
GAME_GRID_SIZE = 10

logging.basicConfig(level=logging.INFO)
game = Game(GAME_GRID_SIZE)

engine = engine = create_engine('postgresql://postgres:q1w2e3@localhost/WEC.db') 
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
    if game.started == False:
        game.start()
        logging.info("Starting game")
        data = {"Result" : "Game started"}
    else:
        data = {"Result" : "Game not started.  Game is already running."}
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
        logging.debug("Closing connection since game is already in progress")
        return ws

    while 1:
        msg = await ws.receive()
        logging.debug(msg)
        if msg.type == aiohttp.WSMsgType.TEXT:
            logging.debug("Received message %s" % msg.data)
            serialized_data = json.loads(msg.data)

            if not validate_team(serialized_data["team_id"], serialized_data["authenticationKey"]): # check if team is who they say they are
                logging.info("Team id and/or token invalid")
                await ws.send_str("The team id and/or token you provided is invalid.")
                break
            logging.debug("Team number %s validated" % serialized_data["team_id"])
            
            handle_request(serialized_data)
            # TODO: Ideally, we send back some sort of response confirming appropriate handling of the request or
            # return some sort of message that indicates a malformed request
            await ws.send_str("Echo: {}".format(msg.data))
        elif msg.type == aiohttp.WSMsgType.CLOSE or\
            msg.type == aiohttp.WSMsgType.ERROR:
                break

    app["sockets"].remove(ws)
    logging.debug("Closed connection.")
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

# TODO: handle player moves (assess validity, etc.) if game has started
# TODO: check if move is legal (i.e. they didn't jump a space and the space they want exists)
def handle_request(messageDict):
    global game
    global session
    if "type" in messageDict and "message" in messageDict and "authenticationKey" in messageDict:
        if messageDict["type"].upper() == "REGISTRATION":
            game.spawn_player(int(messageDict["team_id"]))
            move_queue_dict[messageDict["team_id"]] = MoveQueue(messageDict["team_id"])
        # TODO: test the below
        # TODO: this handles one player's requests. must ensure other player moves in parallel somehow
        elif messageDict["type"].upper() == "MOVE":
            if messageDict["team_id"] not in move_queue_dict:
                logging.info("Unregistered team tried to submit a move")
            else:
                move_queue_dict[messageDict["team_id"]].add_move(messageDict["message"].upper())
        else:
            logging.info("Message with invalid type received: " + messageDict)
    else:
        logging.info("Malformed message received: " + messageDict)
        return
    
def get_json_serialized_game_state():
    global game
    if game.current_game.is_complete == True:
        return("Game Complete: Team " +str(game.current_game.victor) + " won the match")
    return json.dumps(game.game_grid)

# This game loop will run infinitely and will periodically send back a JSON string summarizing game state if game is
# active
async def game_loop(app):
    global game
    global session
    while 1:
        if game.started:
            apply_moves()
            json_game_state = get_json_serialized_game_state()
            if "Game Complete" not in json_game_state:
                print_game_state(get_json_serialized_game_state())
            for ws in app["sockets"]:
                logging.info('Sending game state')
                await ws.send_str(get_json_serialized_game_state())
        await asyncio.sleep(GAME_LOOP_INTERVAL_IN_SECONDS)

def print_game_state(game_state_json):
    game_state_dict = json.loads(game_state_json)
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
            else:
                sys.stdout.write(str(val))
        print("")

def apply_moves():
    for team_id in move_queue_dict:
        team_id = int(team_id)
        queue = move_queue_dict[team_id]
        start, moving_to = move_from_to(team_id, queue.dequeue_oldest_move().upper())
        if game.game_grid[moving_to] != "":
            # the player is dead
            game.current_game.is_complete = True
            if game.game_grid[moving_to] != "wall" and game.game_grid[moving_to] != "trail":
                # both player collided, neither player gets a win
                # TODO: make sure its isn't triggered by one team hitting the trail of the other
                # team by one space (i.e. as the other team was moving out of the way)
                game.current_game.victor = None
                logging.info("Both player collided, neither gets a win")
            else:
                # the other player won
                if game.current_game.team1_id == team_id:  # if we are team1, the other team won
                    game.current_game.victor = game.current_game.team2_id
                    team = session.query(Teams).filter_by(team_id=game.current_game.team2_id).first()
                else:
                    game.current_game.victor = game.current_game.team1_id
                    team = session.query(Teams).filter_by(team_id=game.current_game.team1_id).first()
                logging.info("Team " + str(game.current_game.victor) + " won the match")
                team.games_won += 1
                session.add(team)
            game.stop()
            try:
                session.add(game.current_game)
                session.commit()
            except Exception as e:
                logging.debug(e)
                session.rollback()

        else:  # neither player died so move the player as requested and set their old position as "trail"
            game.update_game_state({start: "trail", moving_to: team_id})

app = web.Application()

# a list of all the active socket connections
app["sockets"] = []

# a dictionary of id - move queue pairs
move_queue_dict = {}

asyncio.ensure_future(game_loop(app))

app.router.add_route("GET", "/connect", wshandler)
app.router.add_route("GET", "/startGame", start_game)
app.router.add_route("GET", "/stopGame", stop_game)


web.run_app(app)

# TODO: disconnects should be handled