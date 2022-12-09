from enum import Enum
import json
import os
import threading
import datetime
import twitch
import gsheets
import settings
from settings import baseDir

class Role(Enum):
    ADMIN = 1
    RACER = 2
    BLACKLIST = 3
    UPDATER = 4

def updateUsersByID():
    print("Updating usernames by id using the Twitch API...")

    with open(os.path.join(baseDir,'users.json'),'r') as f:
        j = json.load(f)
        sets = [ j['admins'], j['updaters'], j['blacklist'], j['test-racers'] ]
    
    for i, s in enumerate(sets):
        s_new = twitch.updateSet(s)
        if s_new != None:
            sets[i] = s_new

    with open(os.path.join(baseDir,'users.json'),'w') as f:
        j['admins'] = sets[0]
        j['updaters'] = sets[1]
        j['blacklist'] = sets[2]
        j['test-racers'] = sets[3]
        json.dump(j, f, indent=4)
    
    global admins, updaters, blacklist
    admins = sets[0]
    updaters = sets[1]
    blacklist = sets[2]

    with open(os.path.join(baseDir,'settings.json'), 'r+') as f:
        j = json.load(f)
        j['last-id-update'] = datetime.datetime.now().isoformat().split(".")[0]
        f.seek(0)
        json.dump(j, f, indent=4)
        f.truncate()

    print("Done updating Twitch usernames.")

def push_all():
    with open(os.path.join(baseDir,'users.json'),'r+') as f:
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
        print("Twitch user not found. Aborting.")
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

def status(user, playerLookup):
    user = user.lower()
    returnString = user + ": "
    if user in playerLookup.keys():
        returnString += "Racer ("+playerLookup[user].status +": "+ str(playerLookup[user].collects) +"), "
    if user in admins:
        returnString += "Admin, "
    if user in updaters:
        returnString += "Updater, "
    if user in blacklist:
        returnString += "Blacklist, "
    if returnString == (user + ": "):
        returnString += "None, "
    return returnString[0:-2]

admins, updaters, blacklist = [], [], []

def init_users():
    global admins, updaters, blacklist
    with open(os.path.join(baseDir,'users.json'),'r') as f:
        j = json.load(f)
        admins = j['admins']
        blacklist = j['blacklist']
        updaters = j['updaters']
        if settings.debug:
            racers = list(j['test-racers'].keys())
    if not settings.debug:
        racers = gsheets.getRacers()
    twitch.fetchProfiles(racers)

    # update usernames by ID if it hasn't been done in the last day
    if (datetime.datetime.now() - settings.last_id_update).total_seconds() > 86400:
        t = threading.Thread(target=updateUsersByID, args=())
        t.daemon = True
        t.start()
    
    return racers
