from datetime import datetime

class IncomingMessage:
    def __init__(self, _type, _message, _status, _source ):
        self.type = _type
        self.message = _message
        self.source = _source
        self.timestamp = datetime.utcnow()