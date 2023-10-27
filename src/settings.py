import datetime
import json
import os
import math
import pygame

def make_dir(dir_path):
    try:
        os.makedirs(path(dir_path))
    except OSError as e:
        pass

def path(file):
    return os.path.join(baseDir, file)

def now():
    return datetime.datetime.now().isoformat().split(".")[0]

def dur_to_str(dur):
    # calculate readable duration string
    negative = False
    if dur < 0:
        dur = dur * -1
        negative = True

    tmp1 = datetime.timedelta(seconds=math.floor(dur))
    delta = str(tmp1).split(" day")

    initialHours = 0
    extraHours=""
    if len(delta)==1:
        extraHours = delta[0]
    elif len(delta)==2:
        days = delta[0]
        days = int(days)
        initialHours = days * 24
        if delta[1][0]=="s":
            extraHours = delta[1][3:]
        elif delta[1][0]==",":
            extraHours = delta[1][2:]

    finalTime = extraHours.split(":")
    finalHours = int(finalTime[0]) + initialHours
    finishTime = str(finalHours)+":"+finalTime[1]+":"+finalTime[2]
    if negative:
        finishTime = "-"+finishTime
    return finishTime

def getFont(size):
    return pygame.font.Font(path("resources/Lobster 1.4.otf"), size)

def set_max_count(num_players):
    global max_count
    max = 99
    i1 = 28
    while True:
        if num_players <= i1:
            break
        max += 100
        i1 += 25
    max_count = max

def save_api_tokens_to_file():
    with open(path('settings.json'), 'r+') as f:
        j = json.load(f)
        j['twitch-api-token'] = twitch_token
        j['twitch-refresh-token'] = twitch_refresh_token
        f.seek(0)
        json.dump(j, f, indent=4)
        f.truncate()

def save_state(player_lookup):
    with open(path('state.json'), 'r+') as f:
        j = json.load(f)
        j['start-time'] = startTime.isoformat().split(".")[0]
        racers = j['racers']
        for player_name in player_lookup.keys():
            player = player_lookup[player_name]
            racer_dict = {}
            racer_dict['score'] = player.score
            racer_dict['status'] = player.status
            racer_dict['finishtime'] = None
            if player.finishTimeAbsolute != None:
                racer_dict['finishtime'] = player.finishTimeAbsolute.isoformat().split(".")[0]
            racers[player.name] = racer_dict
        j['racers'] = racers
        f.seek(0)
        json.dump(j, f, indent=4)
        f.truncate()

def init_state():
    global startTime
    state_file = path("state.json")

    if not os.path.isfile(state_file):
        with open(state_file, 'w+') as f:
            json.dump({"start-time":startTime.isoformat().split(".")[0], "racers":{}}, f, indent=4)
    else:
        with open(state_file, 'r+') as f:
            j = json.load(f)
            if "start-time" not in j:
                j["start-time"] = startTime.isoformat().split(".")[0]
            if "racers" not in j:
                j["racers"] = {}
            startTime = datetime.datetime.fromisoformat(j['start-time'])
            f.seek(0)
            json.dump(j, f, indent=4)
            f.truncate()
    
    dur = (datetime.datetime.now() - startTime).total_seconds()
    if dur > 604800:
        # Start time is >1 week ago. Reset scores and delete profile pictures.
        # Keep old start time to avoid creating erroneous log files.
        with open(state_file, 'r+') as f:
            j = json.load(f)
            j["racers"] = {}
            f.seek(0)
            json.dump(j, f, indent=4)
            f.truncate()
        profiles_dir = path('profiles')
        for filename in os.listdir(profiles_dir):
            filepath = os.path.join(profiles_dir, filename)
            os.remove(filepath)

baseDir = os.path.join(os.path.dirname(__file__),'..')
startTime = datetime.datetime.now()
doQuit = False
redraw = True
debug = False
mode = ""
max_score = 0
gsheet = ""
modeInfo = {}
stopTimer = False
playersLock = False
max_count = 0
blank_profile = pygame.image.load(path("resources/empty.png"))
twitch_pw = ""
twitch_nick = ""
chat_ref = None
sorted_racers = []
auto_stream_events = True
make_dir('irc')
make_dir('log')
make_dir('profiles')
init_state()

with open(path('settings.json'), 'r') as f:
    j = json.load(f)
    test_gsheet = j.get("testing-gsheet", "")
    mode = j['mode']
    modeInfo = j['modes'][mode]
    gsheet = modeInfo['gsheet']
    if test_gsheet != "":
        debug = True
        gsheet = test_gsheet
    for g in modeInfo['games']:
        max_score += g['count']

    extra_chats = j['extra-chat-rooms']

    twitch_clientid = j['twitch-api-clientid']
    twitch_secret = j['twitch-api-secret']
    twitch_token = j['twitch-api-token']
    twitch_refresh_token = j['twitch-refresh-token']
    google_api_key = j['google-api-key']
