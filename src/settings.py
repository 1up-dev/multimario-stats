import datetime
import pygame
import json
import os

baseDir = os.path.join(os.path.dirname(__file__),'../')
startTime = datetime.datetime.now()
doQuit = False
redraw = True
debug = True
mode = ""
max_score = 0
gsheet = ""
modeInfo = {}
with open(os.path.join(baseDir,'settings.json'), 'r') as f:
    j = json.load(f)
    startTime = datetime.datetime.fromisoformat(j['start-time'])
    last_id_update = datetime.datetime.fromisoformat(j['last-id-update'])
    debug = j['debug']

    modeId = j['mode']
    modeInfo = j['modes'][modeId]
    mode = modeInfo['name']
    max_score = modeInfo['max-score']
    gsheet = modeInfo['gsheet']

    twitch_nick = j['bot-twitch-username']
    twitch_pw = j['bot-twitch-auth']
    use_backups = j['use-player-backups']
    extra_chats = j['extra-chat-rooms']

    twitch_token = j['twitch-api-token']
    twitch_clientid = j['twitch-api-clientid']
    twitch_secret = j['twitch-api-secret']

    google_api_key = j['google-api-key']

    srl_nick = j['srl-username']
    srl_pw = j['srl-auth']

def getFont(size):
    return pygame.font.Font(os.path.join(baseDir,"resources/Lobster 1.4.otf"), size)
