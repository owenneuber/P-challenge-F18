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
GAME_GRID_SIZE = 15

logging.basicConfig(level=logging.INFO)
game = Game(GAME_GRID_SIZE)

engine = create_engine('postgresql://postgres:q1w2e3@localhost/WEC.db')
Session = sessionmaker(bind=engine)
session = Session()  # session to use in functions which need it


def validate_team(team_id, token):
    """ Returns True if the team is who they claim to be, False if not. """
    global session
    team = session.query(Teams).filter_by(team_id=team_id).first()
    if team == None:  # i.e. the provided team id does not exist in the db
        return False
    return team.team_key == token


# HTTP endpoint to start game (i.e. sets game_started as true)
async def start_game(request):
    global game
    if game.started == False and len(move_queue_dict) == 2:
        print_game_state()
        for ws in app["sockets"]:
            await ws.send_str(get_json_serialized_game_state())
        await asyncio.sleep(3)
        game.start()
        logging.info("Starting game")
        data = {"Result": "Game started"}
    else:
        data = {"Result": "Game not started."}
    return web.json_response(data)


async def stop_game(request):
    global game
    if game.started == True:
        game.stop()
        logging.info("Stopping game")
        data = {"Result": "Game stopped"}
        # TODO: reset everything - close conns, reset game state, etc.
    else:
        data = {"Result": "Game not stopped.  Game is not running."}
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
            # logging.info("Received message %s" % msg.data)
            try:
                deserialized_data = json.loads(msg.data)
                if not validate_team(deserialized_data["team_id"],
                                     deserialized_data["authenticationKey"]):  # check if team is who they say they are
                    logging.info("Team id and/or token invalid")
                    await ws.send_str("The team id and/or token you provided is invalid.")
                    break
                logging.info("Team number %s validated" % deserialized_data["team_id"])
                try:
                    handle_request(deserialized_data)
                    await ws.send_str("Echo: {}".format(msg.data))
                except ValueError as e:
                    await ws.send_str("Invalid input.  Reason: " + e.args[0])
            except JSONDecodeError:
                logging.info("Non-JSON message received.")

        elif msg.type == aiohttp.WSMsgType.CLOSE or \
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
        elif msg.type == aiohttp.WSMsgType.CLOSE or \
                msg.type == aiohttp.WSMsgType.ERROR:
            break

        if is_valid_message(msg.data):
            await ws.send_str("Valid message.  %s" % msg.data)
            await ws.send_str(json.dumps(test_game_state))
        else:
            await ws.send_str("Invalid message.  %s" % msg.data)

    app["sockets"].remove(ws)
    logging.info("Closed connection.")
    return ws


def move_from_to(team_id, move_direction):
    """Takes in the message of a user who is moving and returns the grid position
    they started in and the one they intend to move to (in a tuple). """
    global game
    original_position = list(game.game_grid.keys())[list(game.game_grid.values()).index(team_id)]  # "row,column"
    new_position = list(map(int, original_position.split(",")))  # [int(row), int(column)]
    if move_direction == "UP":
        new_position[0] -= 1
    elif move_direction == "DOWN":
        new_position[0] += 1
    elif move_direction == "RIGHT":
        new_position[1] += 1
    elif move_direction == "LEFT":
        new_position[1] -= 1
    return (
    original_position, str(new_position[0]) + "," + str(new_position[1]))  # return ("row1,column1", "row2,column2")


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
        if game.started and not game.current_game.is_complete:
            apply_moves()
            print_game_state()
            for ws in app["sockets"]:
                await ws.send_str(get_json_serialized_game_state())
            # if game.current_game.is_complete:
            #    game.stop() Not sure if this should be here
            # If the game is done, should we exit out of this loop? idk
        await asyncio.sleep(GAME_LOOP_INTERVAL_IN_SECONDS)


def print_game_state():
    global game
    game_state_dict = game.game_grid
    game_arr = []
    for i in range(0,GAME_GRID_SIZE + 2):
        new = []
        for j in range(0, GAME_GRID_SIZE + 2):
            new.append("")
        game_arr.append(new)

    for key in game_state_dict:
        pair = key.split(",")
        row = int(pair[0])
        col = int(pair[1])
        game_arr[row][col] = (game_state_dict[key])

    for i in range(0, GAME_GRID_SIZE + 2):
        for j in range(0, GAME_GRID_SIZE + 2):
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
                sys.stdout.write(val.rstrip("_dead") + "D")
            else:
                sys.stdout.write(str(val))
        print("")


def apply_moves():
    team1, team2 = move_queue_dict.items()  # 2 tuples of form: (team_id, MoveQueue object)
    start1, moving_to1 = move_from_to(team1[0], team1[1].dequeue_oldest_move().upper())
    start2, moving_to2 = move_from_to(team2[0], team2[1].dequeue_oldest_move().upper())
    team1_dead = False
    team2_dead = False
    collision = False
    logging.info("team " + str(team1[0]) + ": " + start1 + " --> " + moving_to1)
    logging.info("team " + str(team2[0]) + ": " + start2 + " --> " + moving_to2)

    if moving_to1 == moving_to2:  # they collided!
        team1_dead = True
        team2_dead = True
        game.current_game.victor = None
        logging.info("Both player collided")
        game.update_game_state({start1: "trail", start2: "trail", moving_to1: "collision"})
        game.current_game.is_complete = True
        game.finish(game.current_game.victor)
        return # no need to do anything more here
    else:
        if game.game_grid[moving_to1] != "":
            team1_dead = True

        if game.game_grid[moving_to2] != "":
            team2_dead = True

    if (not team1_dead) and (
    not team2_dead):  # neither player died so move the player as requested and set their old position as "trail"
        game.update_game_state({start1: "trail", start2: "trail", moving_to1: team1[0], moving_to2: team2[0]})
        return  # the rest of the function can be skipped if both players lived

    if team1_dead and team2_dead:
        game.current_game.victor = None
        logging.info("Both player died at the same time. Neither team wins.")
        game.update_game_state({start1: "trail", start2: "trail", moving_to1: str(team1[0]) + "_dead",
                                moving_to2: str(team2[0]) + "_dead"})
    elif team1_dead:
        game.current_game.victor = int(team2[0])
        game.update_game_state(
            {start1: "trail", start2: "trail", moving_to1: str(team1[0]) + "_dead", moving_to2: team2[0]})
    elif team2_dead:
        game.current_game.victor = int(team1[0])
        game.update_game_state(
            {start1: "trail", start2: "trail", moving_to1: team1[0], moving_to2: str(team2[0]) + "_dead"})

    if game.current_game.victor:
        logging.info("Team " + str(game.current_game.victor) + " won the match")

    game.current_game.is_complete = True
    game.finish(game.current_game.victor)


def is_valid_message(serialized_message):
    try:
        deserialized_data = json.loads(serialized_message)
        if ("type" not in deserialized_data or "message" not in deserialized_data \
            or "authenticationKey" not in deserialized_data or "team_id" not in deserialized_data) and len(
            deserialized_data) == 2:
            return False
        if deserialized_data["type"].upper() == "MOVE" and deserialized_data["message"].upper() not in (
        "LEFT", "RIGHT", "UP", "DOWN"):
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

test_game_state = {"15,2": "", "5,15": "", "3,12": "", "15,9": "", "11,7": "", "16,5": "wall", "5,9": "", "16,0": "wall", "8,2": "", "6,14": "", "15,4": "", "14,10": "", "2,0": "wall", "8,7": "", "14,8": "", "9,8": "", "12,1": "", "11,13": "", "7,15": "", "1,12": "", "4,2": "", "13,11": "", "0,1": "wall", "12,4": "", "14,5": "", "0,3": "wall", "3,5": "", "7,8": "", "12,14": "", "14,14": "", "10,12": "", "10,13": "", "3,3": "", "14,12": "", "12,6": "", "3,4": "", "10,14": "", "8,6": "", "6,13": "", "14,16": "wall", "7,2": "trail", "9,12": "", "2,14": "", "5,0": "wall", "11,8": "", "15,16": "wall", "15,0": "wall", "7,3": 1, "1,5": "", "4,4": "", "11,6": "", "6,4": "", "1,8": "", "13,1": "", "8,11": "", "8,9": "", "11,3": "", "3,14": "", "14,9": "", "4,6": "", "8,0": "wall", "13,9": "", "16,3": "wall", "14,3": "", "1,2": "", "11,14": "", "8,15": "", "0,8": "wall", "1,9": "", "5,3": "", "7,13": 2, "9,2": "", "7,0": "wall", "7,11": "", "10,8": "", "6,5": "", "14,13": "", "16,8": "wall", "12,3": "", "6,11": "", "10,2": "", "8,13": "", "9,7": "", "10,15": "", "15,14": "", "14,1": "", "6,9": "", "16,11": "wall", "6,15": "", "11,12": "", "9,1": "", "15,3": "", "5,11": "", "1,7": "", "0,5": "wall", "3,8": "", "15,10": "", "2,4": "", "2,12": "", "9,4": "", "11,11": "", "11,1": "", "12,8": "", "5,8": "", "4,13": "", "0,14": "wall", "10,9": "", "3,9": "", "9,0": "wall", "10,6": "", "8,10": "", "7,10": "", "0,10": "wall", "15,7": "", "2,11": "", "0,16": "wall", "2,9": "", "0,9": "wall", "1,4": "", "13,8": "", "6,12": "", "13,10": "", "16,2": "wall", "16,1": "wall", "2,7": "", "13,7": "", "6,8": "", "7,6": "", "1,14": "", "12,10": "", "2,6": "", "1,11": "", "3,6": "", "7,7": "", "13,5": "", "5,4": "", "15,6": "", "4,5": "", "16,7": "wall", "8,8": "", "8,1": "", "10,4": "", "11,2": "", "12,0": "wall", "16,14": "wall", "14,7": "", "0,2": "wall", "15,13": "", "2,2": "", "2,13": "", "10,10": "", "14,0": "wall", "5,13": "", "2,15": "", "9,14": "", "12,12": "", "5,12": "", "1,3": "", "1,10": "", "4,1": "", "13,0": "wall", "4,3": "", "3,13": "", "6,7": "", "12,15": "", "7,14": "trail", "8,14": "", "6,1": "", "3,1": "", "2,5": "", "0,11": "wall", "8,12": "", "9,9": "", "16,10": "wall", "9,10": "", "7,12": "", "6,6": "", "13,3": "", "1,6": "", "1,1": "", "0,6": "wall", "12,16": "wall", "15,12": "", "6,3": "", "0,15": "wall", "10,3": "", "6,10": "", "10,16": "wall", "10,0": "wall", "3,10": "", "2,16": "wall", "7,16": "wall", "0,4": "wall", "16,4": "wall", "12,13": "", "3,7": "", "13,16": "wall", "4,15": "", "10,7": "", "13,2": "", "13,13": "", "1,0": "wall", "11,10": "", "12,9": "", "13,4": "", "13,6": "", "11,15": "", "5,5": "", "0,13": "wall", "13,12": "", "1,13": "", "11,16": "wall", "6,0": "wall", "11,0": "wall", "2,8": "", "5,2": "", "4,8": "", "5,16": "wall", "1,16": "wall", "0,12": "wall", "4,14": "", "8,3": "", "14,2": "", "9,13": "", "3,0": "wall", "4,0": "wall", "4,9": "", "4,11": "", "16,15": "wall", "7,1": "", "2,10": "", "3,15": "", "14,15": "", "12,11": "", "12,7": "", "15,5": "", "11,4": "", "9,16": "wall", "10,11": "", "12,2": "", "7,5": "", "15,15": "", "10,5": "", "9,6": "", "9,5": "", "3,11": "", "14,11": "", "14,6": "", "9,3": "", "8,4": "", "6,2": "", "9,15": "", "12,5": "", "4,10": "", "7,9": "", "16,12": "wall", "5,1": "", "11,9": "", "11,5": "", "13,14": "", "2,1": "", "5,10": "", "16,9": "wall", "4,12": "", "14,4": "", "3,16": "wall", "5,7": "", "3,2": "", "15,11": "", "16,16": "wall", "4,16": "wall", "8,16": "wall", "5,14": "", "8,5": "", "1,15": "", "5,6": "", "10,1": "", "0,7": "wall", "16,13": "wall", "15,8": "", "4,7": "", "6,16": "wall", "9,11": "", "7,4": "", "2,3": "", "13,15": "", "16,6": "wall", "15,1": "", "0,0": "wall"}


asyncio.ensure_future(game_loop(app))

app.router.add_route("GET", "/connect", wshandler)
app.router.add_route("GET", "/connect_dev", dev_wshandler)
app.router.add_route("GET", "/startGame", start_game)
app.router.add_route("GET", "/stopGame", stop_game)

web.run_app(app)