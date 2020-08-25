from enum import Enum
import json
import twitch
import google_sheets

class Role(Enum):
    ADMIN = 1
    RACER = 2
    BLACKLIST = 3
    UPDATER = 4

def load_all():
    with open('settings.json','r') as f:
        j = json.load(f)
        debug = json.loads(j['debug'].lower())
        test_racers = j['test-racers-short']
    
    if not debug:
        twitch.updateUsernamesByID()

    with open('users.json','r') as f:
        j = json.load(f)
        global admins, blacklist, updaters
        admins = j['admins']
        blacklist = j['blacklist']
        updaters = j['updaters']
    
    #load racers
    global racersCS
    if debug:
        racersCS = list(test_racers.keys())
    else:
        racersCS = google_sheets.getRacers()
        for r in racersCS:
            if r.lower() not in updaters:
                add(r.lower(), Role.UPDATER)
    print("Racers: " + str(racersCS))
    global racersL
    racersL = []
    for racer in racersCS:
        racersL.append(racer.lower())

def push_all():
    with open('users.json','w') as f:
        j = {'admins': admins, 'blacklist': blacklist, 'updaters': updaters}
        json.dump(j, f, indent=4)

def add(user, role: Role):
    id = twitch.getTwitchId(user)
    if id == None:
        print("Twitch user not found. Aborting.")
        return
    if role == Role.UPDATER:
        updaters[user] = id
    elif role == Role.ADMIN:
        admins[user] = id
    elif role == Role.BLACKLIST:
        blacklist[user] = id
    push_all()

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

load_all()
