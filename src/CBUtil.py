import json

def isJson(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True

def checkToken(token):
    if len(token) != 20:
        return False
    else:
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!*/-|"
        for char in token:
            if char not in allowed:
                return False
        return True