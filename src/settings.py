import datetime
import json
import os
import math
import traceback
import pygame

def make_dir(path):
    try:
        os.makedirs(os.path.join(baseDir,path))
    except OSError as e:
        pass

baseDir = os.path.join(os.path.dirname(__file__),'..')
startTime = datetime.datetime.now()
doQuit = False
redraw = True
debug = True
mode = ""
max_score = 0
gsheet = ""
modeInfo = {}
stopTimer = False
playersLock = False
max_count = 0
make_dir('irc')
make_dir('log')
make_dir('profiles')
with open(os.path.join(baseDir,'settings.json'), 'r') as f:
    j = json.load(f)
    debug = j['debug']
    mode = j['mode']
    modeInfo = j['modes'][mode]
    gsheet = modeInfo['gsheet']
    if debug:
        gsheet = j['debug-gsheet']
    for g in modeInfo['games']:
        max_score += g['count']
    
    use_backups = j['use-player-backups']
    startTime = datetime.datetime.fromisoformat(j['start-time'])
    
    twitch_nick = j['bot-twitch-username']
    twitch_pw = j['bot-twitch-auth']
    extra_chats = j['extra-chat-rooms']

    twitch_clientid = j['twitch-api-clientid']
    twitch_secret = j['twitch-api-secret']
    twitch_token = j['twitch-api-token']
    last_id_update = datetime.datetime.fromisoformat(j['last-id-update'])
    google_api_key = j['google-api-key']

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
    return pygame.font.Font(os.path.join(baseDir,"resources/Lobster 1.4.otf"), size)

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