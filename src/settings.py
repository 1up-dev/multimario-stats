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
with open('settings.json', 'r') as f:
    j = json.load(f)
    startTime = datetime.datetime.fromisoformat(j['start-time'])
    debug = j['debug']

    modeId = j['mode']
    modeInfo = j['modes'][modeId]
    mode = modeInfo['name']
    max_score = modeInfo['max-score']
    gsheet = modeInfo['gsheet']

def getFont(size):
    return pygame.font.Font("./resources/Lobster 1.4.otf", size)
