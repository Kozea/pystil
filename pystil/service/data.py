from datetime import datetime

class Message(object):

    def __init__(self, query, user_agent, remote_addr):
        self.query = query
        self.stamp = datetime.now()
        self.user_agent = user_agent
        self.remote_addr = remote_addr
