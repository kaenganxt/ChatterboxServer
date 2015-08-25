
class SocketData():

    def __init__(self, id, token, obj, type):
        self.id = id
        self.token = token
        self.socket = obj
        self.type = type
        self.sids = dict()
        self.waiting = {"sid":-1}

    def inSids(self, sid):
        return sid in self.sids

    def getSid(self, sid):
        return self.sids[sid]
    
    def getType(self):
        return self.type
    
    def getToken(self):
        return self.token

    def newSid(self, sid):
        self.sids[sid] = SidData(self, sid)

    def removeSid(self, sid):
        del self.sids[sid]
        
    def getSocket(self):
        return self.socket
    
    def getId(self):
        return self.id
    
    def setWaiting(self, object, sid):
        self.waiting = {"conn": object, "sid": sid}
        
    def isWaiting(self):
        return self.waiting["sid"] != -1
    
    def getWaiting(self):
        return self.waiting
    
    def resetWaiting(self):
        self.waiting = {"sid": -1}
        
    def getSids(self):
        return self.sids

class SidData():

    def __init__(self, socket, sid):
        self.id = sid
        self.socket = socket
        self.status = "none"
        self.conn = "none"

    def hasConn(self):
        return self.conn != "none"

    def getConn(self):
        return self.conn

    def getStatus(self):
        return self.status

    def getSocket(self):
        return self.socket

    def getId(self):
        return self.id
    
    def setStatus(self, status):
        self.status = status
        
    def setConn(self, conn):
        self.conn = conn
