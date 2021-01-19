import datetime
import pygame
import json

startTime = datetime.datetime.now()
doQuit = False
redraw = True
debug = True
mode = ""
max_score = 0
gsheet = ""
with open('settings.json', 'r') as f:
    j = json.load(f)
    startTime = datetime.datetime.fromisoformat(j['start-time'])
    debug = j['debug']
    mode = j['mode']['name']
    max_score = j['mode']['max-score']
    gsheet = j['mode']['gsheet']

def getFont(size):
    return pygame.font.Font("./resources/Lobster 1.4.otf", size)
