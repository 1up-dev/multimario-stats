import random
import os
import datetime
import urllib
import json
import threading
import pygame
import gsheets
import settings
import twitch

class Player:
    def __init__(self, name, state_data):
        self.name = name.lower()
        self.display_name = name
        self.twitch_id = ""
        self.corner = (0,0)
        self.place = 1
        self.score = 0
        self.duration_str = ""
        self.duration = 0
        self.finishTimeAbsolute = None
        self.status = "live"
        self.profile = settings.blank_profile
        if state_data == {} and settings.debug:
            self.score = random.choice(range(0, settings.max_score))
        if state_data != {}:
            self.score = state_data['score']
            if self.score > settings.max_score:
                self.score = 0
            self.status = state_data['status']
            if state_data['finishtime'] != None:
                self.finishTimeAbsolute = datetime.datetime.fromisoformat(state_data['finishtime'])
            self.calculateDuration()
    
    def collected(self):
        # construct "has collected" message
        games = settings.modeInfo['games']
        game, collectible = "", ""
        score = self.score
        for g in games:
            if score <= g['count']:
                game = g['name']
                collectible = g['collectible']
                break
            score -= g['count']
        if score != 1:
            if collectible[-1] == 'y':
                collectible = collectible[:-1] + "ies"
            else:
                collectible += "s"
        return (score, collectible, game)

    def calculateDuration(self):
        # calculate duration in seconds from finishTime - startTime
        if self.finishTimeAbsolute == None:
            return
        self.duration = (self.finishTimeAbsolute - settings.startTime).total_seconds()
        self.duration_str = settings.dur_to_str(self.duration)

    def finish(self, status):
        self.status = status
        self.finishTimeAbsolute = datetime.datetime.now()
        self.calculateDuration()

def get_player_infos(logins, playerLookup):
    user_infos = twitch.get_user_infos(logins)
    for info in user_infos:
        login = info['login']
        racer = playerLookup[login]
        path = settings.path(f"profiles/{racer.name}.png")
        if not os.path.isfile(path):
            urllib.request.urlretrieve(info['profile_image_url'], path)
        try:
            racer.profile = pygame.image.load(path)
        except pygame.error as e:
            # remove corrupted profile image (possibly from closing the program while a download is in progress)
            os.remove(path)
            urllib.request.urlretrieve(info['profile_image_url'], path)
        racer.twitch_id = info['id']
        racer.display_name = info['display_name']
        if racer.display_name.lower() != racer.name:
            racer.display_name = racer.name
        settings.redraw = True

def get_player_infos_async(logins, playerLookup):
    t = threading.Thread(target=get_player_infos, args=(logins, playerLookup,))
    t.daemon = True
    t.start()

def init_players():
    # initialize racers
    if 'race-num' in settings.modeInfo:
        race_num = settings.modeInfo['race-num']
        column = chr(ord('A') + race_num)
        settings.gsheet = settings.gsheet.replace('A6:A?', f'A6:{column}?')
    racers = gsheets.getRacers()
    playerLookup = {}
    state_file = settings.path("state.json")
    with open(state_file, 'r') as f:
        j = json.load(f)['racers']
    for racer in racers:
        state_data = {}
        if j != {} and racer.lower() in j.keys():
            state_data = j[racer.lower()]
        playerLookup[racer.lower()] = Player(racer, state_data)
    get_player_infos_async(list(playerLookup.keys()), playerLookup)

    # determine number of pages
    settings.set_max_count(len(playerLookup))

    return playerLookup
