# Each client player should have a move queue.  Every move sent from a client should be appended to the queue.
# The periodic move task (every 1 second) will flush the oldest move from the queue
import logging
import queue

class MoveQueue:
    def __init__(self, _teamId):
        MAX_MOVE_QUEUE_SIZE = 100;
        self.teamId = _teamId
        self.moveQueue = queue.Queue(MAX_MOVE_QUEUE_SIZE)

    def add_move(self, move):
        self.moveQueue.put(move)

    def dequeue_oldest_move(self):
        if self.moveQueue.empty():
            logging.info("Defaulting to UP")
            return "UP" # default to UP if the queue is empty
        move = self.moveQueue.get()
        logging.info("Team %s executes %s move." % (self.teamId, str(move)))
        return move

    def print(self):
        for elem in list(self.moveQueue.queue):
            print(elem)