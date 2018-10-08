import json

class Message:
    def __init__(self, _type, _message, _status=200):
        self.type = _type
        self.message = _message
        self.status = _status

    def serialize(self):
        return json.dump(self)