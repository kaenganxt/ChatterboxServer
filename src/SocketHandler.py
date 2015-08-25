import json
import random
import CBUtil
from SocketData import SocketData

connId = 0
conns = dict()
storagerByStr = dict()

def open(type, token, socket):
    global connId
    if type == "storager" and not CBUtil.checkToken(token):
        socket.write_message(json.dumps({"action": "close", "type": "invalidToken"}))
        socket.close()
        return
    connId += 1
    socket.id = connId
    addConn(SocketData(connId, token, socket, type))
        
def message(socket, msg, sid):
    global conns
    global storagerByStr
    action = msg["action"]
    sock = socket.getSocket()
    if action == "new":
        socket.newSid(msg["id"])
        return
    elif action == "clearStatus":
        if sid.hasConn():
            other = sid.getConn()
            other.getSocket().removeSid(other.getId())
        me.removeSid(sid.getId())
        return
    elif action == "forward":
        if not sid.hasConn():
            sock.write_message(json.dumps({"action": "forwardError", "sid": msg["sid"], "type": "noConn"}))
            return
        newSid = sid.getConn()
        msg["sid"] = newSid.getId()
        msg["action"] = msg["forwardAction"]
        msg["forwardAction"] = "forwarded"
        newSid.getSocket().getSocket().write_message(json.dumps(msg))
        return
    elif action == "reserve":
        if sid.getStatus() != "none":
            socket.write_message(json.dumps({"action":"reserve", "type": msg["type"], "status": "error", "sid": msg["sid"]}))
            return
        if msg["type"] == "relay" and not "id" in msg:
            count = 0
            relays = getRelays()
            checked = []
            size = len(relays)
            while 1:
                if count == size:
                    break
                id = random.randrange(size)
                if id in checked:
                    continue
                checked.append(id)
                count += 1
                relay = relays[id]
                if relay.getId() in msg["not"]:
                    continue
                relay.getSocket().write_message(json.dumps({"action":"new", "type": socket.getType(), "id": socket.getId()}))
                relay.setWaiting(socket, msg["sid"]);
                sid.setStatus("waiting")
                sid.setConn(relay)
                return
            sock.write_message(json.dumps({"action":"reserve", "type": msg["type"], "status": "no", "sid": msg["sid"]}))
            return
        else:
            if not "id" in msg:
                sock.write_message(json.dumps({"action":"reserve", "type": msg["type"], "status": "error", "sid": msg["sid"]}))
                return
            returnInfo = -1
            if msg["type"] == "storager":
                if msg["id"] in storagerByStr:
                    returnInfo = storagerByStr[msg["id"]]
            else:
                for conn in conns:
                    conn = getConn(conn)
                    if conn.getType() != msg["type"]:
                        continue
                    if conn.getId() != int(msg["id"]):
                        continue
                    returnInfo = conn
            if returnInfo == -1:
                sock.write_message(json.dumps({"action":"reserve", "type": msg["type"], "status": "no", "sid": msg["sid"]}))
                return
            else:
                returnInfo.getSocket().write_message(json.dumps({"action":"new", "type": socket.getType(), "id": socket.getId()}))
                returnInfo.setWaiting(socket, msg["sid"])
                sid.setStatus("waiting")
                sid.setConn(returnInfo)
                return
    elif action == "reserved":
        if sid.getStatus() != "none":
            return
        if not socket.isWaiting():
            sock.write_message(json.dumps({"action":"connClose", "sid": msg["sid"]}))
            return
        nextSid = socket.getWaiting()
        otherSid = nextSid["conn"].getSid(nextSid["sid"])
        otherSid.setStatus("busy")
        otherSid.setConn(sid)
        sid.setStatus("busy")
        sid.setConn(otherSid)
        nextSid["conn"].getSocket().write_message(json.dumps({"action":"reserve", "type": socket.getType(), "status": "ok", "sid": otherSid.getId(), "id": socket.getId()}))
        socket.resetWaiting()
        return
    elif action == "getlist":
        list = []
        count = 0
        for client in conns:
            client = getConn(client)
            if client.getType() == msg["type"]:
                if client.getType() == "storager":
                    list.append(client.getToken())
                else:
                    list.append(client.getId())
                count += 1
                if "count" in msg and count >= msg["count"]:
                    break
        status = "ok"
        if count == 0:
            status = "error"
        spId = -1
        if "spId" in msg:
            spId = msg["spId"]
        sock.write_message(json.dumps({"action": "getlist", "status": status, "ids": list, "spId": spId}))
    elif action == "status":
        for client in conns:
            client = getConn(client)
            if client.getType() != msg["type"]:
                continue
            if msg["type"] == "storager":
                if msg["id"] != client.getToken():
                    continue
            else:
                if msg["id"] != client.getId():
                    continue
            sock.write_message(json.dumps({"action": "status", "type": msg["type"], "classId": msg["classId"], "status": "available", "id": msg["id"]}))
            return
        sock.write_message(json.dumps({"action": "status", "type": msg["type"], "classId": msg["classId"], "status": "notfound"}))
    elif action == "userid":
        sock.write_message(json.dumps({"action": "userid", "id": socket.getId()}))
        
def closeSids(conn):
    global conns
    for sid in conn.getSids():
        sid = conn.getSid(sid)
        if sid.getStatus() == "busy":
            try:
                sid.getSocket().getSocket().write_message(json.dumps({"action":"connClose", "type": conn.getType(), "id": conn.getId(), "sid": sid.getConn().getId()}))
            except:
                pass
        elif sid.getStatus() == "waiting" and sid.getConn().getSocket() in conns:
            sid.getConn().getSocket().resetWaiting()
        if sid.getConn() == "none":
            continue
        if sid.getConn().getSocket() in conns:
            sid.getConn().getSocket().removeSid(sid.getId())
        
def addConn(socketData):
    global conns
    conns[socketData.getId()] = socketData
    if socketData.getType() == "storager":
        global storagerByStr
        storagerByStr[socketData.getToken()] = socketData
        
def removeConn(conn):
    global conns
    if conn.getType() == "storager":
        global storagerByStr
        del storagerByStr[conn.getToken()]
    del conns[conn.getId()]
        
def getConn(id):
    global conns
    return conns[id]

def getRelays():
    global conns
    id = 0
    answer = dict()
    for client in conns:
        client = getConn(client)
        if client.getType() == "relay":
            answer[id] = client
            id += 1
    return answer