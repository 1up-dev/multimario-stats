from enum import Enum
import json
import os
import threading
import datetime
import twitch
import gsheets
import settings
import player

class Role(Enum):
    ADMIN = 1
    RACER = 2
    BLACKLIST = 3
    UPDATER = 4

admins, updaters, blacklist = [], [], []

def updateUsersByID():
    print("Updating usernames by id using the Twitch API...")

    with open(os.path.join(settings.baseDir,'users.json'),'r') as f:
        j = json.load(f)
        sets = [ j['admins'], j['updaters'], j['blacklist'], j['test-racers'] ]
    
    for i, s in enumerate(sets):
        s_new = twitch.updateSet(s)
        if s_new != None:
            sets[i] = s_new

    with open(os.path.join(settings.baseDir,'users.json'),'w') as f:
        j['admins'] = sets[0]
        j['updaters'] = sets[1]
        j['blacklist'] = sets[2]
        j['test-racers'] = sets[3]
        json.dump(j, f, indent=4)
    
    global admins, updaters, blacklist
    admins = sets[0]
    updaters = sets[1]
    blacklist = sets[2]

    with open(os.path.join(settings.baseDir,'settings.json'), 'r+') as f:
        j = json.load(f)
        j['last-id-update'] = datetime.datetime.now().isoformat().split(".")[0]
        f.seek(0)
        json.dump(j, f, indent=4)
        f.truncate()

    print("Done updating Twitch usernames.")

def push_all():
    with open(os.path.join(settings.baseDir,'users.json'),'r+') as f:
        j = json.load(f)
        j['admins'] = admins
        j['blacklist'] = blacklist
        j['updaters'] = updaters
        f.seek(0)
        json.dump(j, f, indent=4)
        f.truncate()

def add(user, role: Role):
    id = twitch.getTwitchId(user)
    if id == None:
        return False
    if role == Role.UPDATER:
        updaters[user] = id
    elif role == Role.ADMIN:
        admins[user] = id
    elif role == Role.BLACKLIST:
        blacklist[user] = id
    push_all()
    return True

def remove(user, role: Role):
    if role == Role.UPDATER:
        if user in updaters:
            del updaters[user]
            print("Removed user "+user+".")
    elif role == Role.ADMIN:
        if user in admins:
            del admins[user]
            print("Removed user "+user+".")
    elif role == Role.BLACKLIST:
        if user in blacklist:
            del blacklist[user]
            print("Removed user "+user+".")
    push_all()

def roles(user, playerLookup):
    user = user.lower()
    out = ""
    if user in admins:
        out += "Admin, "
    if user in updaters:
        out += "Updater, "
    if user in blacklist:
        out += "Blacklist, "
    if user in playerLookup.keys():
        p = playerLookup[user]
        score, collectible, game = p.collected()
        if out != "":
            out = f"Roles: {out}"
        out = f"{p.nameCaseSensitive} has {str(score)} {collectible} in {game} (Place #{p.place}, {p.status}, {p.score}). {out[0:-2]}"
    else:
        if out == "":
            out =  "None, "
        out = f"{user}: {out[0:-2]}"
    return out

def init_users():
    global admins, updaters, blacklist
    with open(os.path.join(settings.baseDir,'users.json'),'r') as f:
        j = json.load(f)
        admins = j['admins']
        blacklist = j['blacklist']
        updaters = j['updaters']
        if settings.debug:
            racers = list(j['test-racers'].keys())
    if not settings.debug:
        racers = gsheets.getRacers()

    # update usernames by ID if it hasn't been done in the last day
    if (datetime.datetime.now() - settings.last_id_update).total_seconds() > 86400:
        t = threading.Thread(target=updateUsersByID, args=())
        t.daemon = True
        t.start()
    
    # player object instantiation
    playerLookup = {}
    backupFile = os.path.join(settings.baseDir,"backup.json")
    if not os.path.isfile(backupFile):
        # create backup file if it doesn't exist
        with open(backupFile, 'w+') as f:
            json.dump({}, f, indent=4)
    with open(backupFile, 'r') as f:
        j = json.load(f)
    for racer in racers:
        state_data = {}
        if settings.use_backups and j != {} and racer.lower() in j.keys():
            state_data = j[racer.lower()]
        playerLookup[racer.lower()] = player.Player(racer, state_data)
    return playerLookup
    
# log 1 update by user id for racer
def log(id, user, racer):
    if id == "":
        return
    # create file if it doesn't exist
    if not os.path.isfile('update-log.json'):
        with open('update-log.json', 'w+') as f:
            json.dump({}, f, indent=4)
    with open(os.path.join(settings.baseDir,'update-log.json'),'r') as f:
        udlog = json.load(f)

    if id in udlog.keys():
        udlog[id]["user"] = user
        udlog[id]["total"] += 1
        if racer in udlog[id]["by-racer"].keys():
            udlog[id]["by-racer"][racer] += 1
        else:
            udlog[id]["by-racer"][racer] = 1
    else:
        # construct user object
        udlog[id] = {"user":user, "total":1, "by-racer":{racer:1}}
    
    with open(os.path.join(settings.baseDir,'update-log.json'),'w') as f:
        json.dump(udlog, f, indent=4)
