from enum import Enum
import json
import os
import threading
import twitch
import gsheets
import settings
import player

class Role(Enum):
    ADMIN = 1
    RACER = 2
    BLOCKLIST = 3
    COUNTER = 4

admins, counters, blocklist = {}, {}, {}

def push_all():
    with open(settings.path('users.json'),'r+') as f:
        j = json.load(f)
        j['admins'] = admins
        j['blocklist'] = blocklist
        j['counters'] = counters
        f.seek(0)
        json.dump(j, f, indent=4)
        f.truncate()

def add(user, user_id, role: Role):
    if role == Role.COUNTER:
        counters[user_id] = user
    elif role == Role.ADMIN:
        admins[user_id] = user
    elif role == Role.BLOCKLIST:
        blocklist[user_id] = user
    push_all()

def remove(user_id, role: Role):
    if role == Role.COUNTER:
        if user_id in counters:
            del counters[user_id]
    elif role == Role.ADMIN:
        if user_id in admins:
            del admins[user_id]
    elif role == Role.BLOCKLIST:
        if user_id in blocklist:
            del blocklist[user_id]
    push_all()

def roles(user_name, user_id, display_name, playerLookup):
    user_roles = []
    if user_id in admins:
        user_roles.append("Admin")
    if user_name.lower() in playerLookup.keys():
        user_roles.append("Racer")
    if user_id in counters:
        user_roles.append("Counter")
    if user_id in blocklist:
        user_roles.append("Blocked")
    if user_roles == []:
        user_roles.append("None")
    return f"{display_name}: {', '.join(user_roles)}"

def init_users():
    global admins, counters, blocklist
    with open(settings.path('users.json'),'r') as f:
        j = json.load(f)
        admins = j['admins']
        blocklist = j['blocklist']
        counters = j['counters']
    if 'race-num' in settings.modeInfo:
        race_num = settings.modeInfo['race-num']
        column = chr(ord('A') + race_num)
        settings.gsheet = settings.gsheet.replace('A6:A?', f'A6:{column}?')
    racers = gsheets.getRacers()
    
    # player object instantiation
    playerLookup = {}
    state_file = settings.path("state.json")
    with open(state_file, 'r') as f:
        j = json.load(f)['racers']
    for racer in racers:
        state_data = {}
        if j != {} and racer.lower() in j.keys():
            state_data = j[racer.lower()]
        playerLookup[racer.lower()] = player.Player(racer, state_data)
    twitch.get_player_infos_async(list(playerLookup.keys()), playerLookup)
    return playerLookup
