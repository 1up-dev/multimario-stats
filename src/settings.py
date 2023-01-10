import datetime
import json
import os
import math

baseDir = os.path.join(os.path.dirname(__file__),'../')
startTime = datetime.datetime.now()
doQuit = False
redraw = True
debug = True
playersLock = False
mode = ""
max_score = 0
gsheet = ""
modeInfo = {}
test_racers = []
stopTimer = False
with open(os.path.join(baseDir,'settings.json'), 'r') as f:
    j = json.load(f)
    startTime = datetime.datetime.fromisoformat(j['start-time'])
    last_id_update = datetime.datetime.fromisoformat(j['last-id-update'])
    debug = j['debug']

    mode = j['mode']
    modeInfo = j['modes'][mode]
    gsheet = modeInfo['gsheet']
    for g in modeInfo['games']:
        max_score += g['count']

    twitch_nick = j['bot-twitch-username']
    twitch_pw = j['bot-twitch-auth']
    use_backups = j['use-player-backups']
    extra_chats = j['extra-chat-rooms']
    test_racers = j['test-racers']

    twitch_token = j['twitch-api-token']
    twitch_clientid = j['twitch-api-clientid']
    twitch_secret = j['twitch-api-secret']
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