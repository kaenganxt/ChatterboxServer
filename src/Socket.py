import json
import CBUtil
import SocketHandler
from tornado.websocket import WebSocketHandler

class Socket(WebSocketHandler):

    def open(self, *args):
        connType = self.get_argument("type")
        token = ""
        if connType == "storager":
            token = self.get_argument("token")
        SocketHandler.open(connType, token, self)

    def on_message(self, message):
        if not CBUtil.isJson(message): return
        msg = json.loads(message)
        me = SocketHandler.getConn(self.id)
        sid = -1
        if "sid" in msg:
            if not me.inSids(msg["sid"]):
                return
            sid = me.getSid(msg["sid"])
        SocketHandler.message(me, msg, sid)

    def on_close(self):
        obj = SocketHandler.getConn(self.id)
        SocketHandler.closeSids(obj)
        SocketHandler.removeConn(obj)

    def check_origin(self, origin):
        print(origin)
        return True
