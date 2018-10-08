# Each client player should have a move queue.  Every move sent from a client should be appended to the queue.
# The periodic move task (every 1 second) will flush the oldest move from the queue

import queue

class MoveQueue:
    MAX_MOVE_QUEUE_SIZE = 100;
    moveQueue = queue.Queue(MAX_MOVE_QUEUE_SIZE)

    def __init__(self, _teamId):
        self.teamId = _teamId

    def add_move(self, move):
        self.moveQueue.put(move)

    def pop_oldest_move(self):
        return self.moveQueue.get()