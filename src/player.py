import random
import os
import pygame
import time
import datetime
import math
import chatroom
import json
import mode
import settings
import sort

class Player:
    def __init__(self, name, state_data):
        self.name = name.lower()
        self.nameCaseSensitive = name
        self.corner = (0,0)
        self.place = 1
        self.score = 0
        self.duration_str = ""
        self.duration = -1
        self.finishTimeAbsolute = None
        self.status = "live"
        if state_data == {} and settings.debug:
            self.score = random.choice(range(0, settings.max_score))
        if state_data != {}:
            self.score = state_data['score']
            self.status = state_data['status']
            if state_data['finishtime'] != None:
                self.finishTimeAbsolute = datetime.datetime.fromisoformat(state_data['finishtime'])
            self.calculateDuration()
        
        try:
            self.profile = pygame.image.load(os.path.join(settings.baseDir,f"profiles/{self.name}.png"))
        except pygame.error:
            self.profile = pygame.image.load(os.path.join(settings.baseDir,"resources/error.png"))

    def update(self, count, playerLookup):
        if self.status == "live":
            if 0 <= count < settings.max_score:
                self.score = count
                # sort() reassigns place numbers so the command output will be accurate
                sort.sort(playerLookup)
                return self.nameCaseSensitive + mode.hasCollected(self.score) + " (Place: #" + str(self.place) + ")"
            elif count == settings.max_score:
                self.score = count
                self.finish("done")
                return self.nameCaseSensitive + " has finished!"
        return ""

    def calculateDuration(self):
        # calculate duration in seconds from finishTime - startTime
        if self.finishTimeAbsolute == None:
            return
        self.duration = (self.finishTimeAbsolute - settings.startTime).total_seconds()

        # calculate readable duration string
        tmp1 = datetime.timedelta(seconds=math.floor(self.duration))
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
        self.duration_str = finishTime

    def finish(self, status):
        self.status = status
        self.finishTimeAbsolute = datetime.datetime.now()
        self.calculateDuration()
    
    def backup(self):
        p = {}
        p['score'] = self.score
        p['status'] = self.status
        if self.finishTimeAbsolute == None:
            p['finishtime'] = None
        else:
            p['finishtime'] = self.finishTimeAbsolute.isoformat()
        
        with open(os.path.join(settings.baseDir,'backup.json'), 'r+') as f:
            j = json.load(f)
            j[self.name] = p
            f.seek(0)
            json.dump(j, f, indent=4)
            f.truncate()
