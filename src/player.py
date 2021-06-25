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

class Player:
    def __init__(self, name, state_data):
        self.name = name.lower()
        self.nameCaseSensitive = name
        self.corner = (0,0)
        self.place = 1
        if state_data == {}:
            self.collects = 0
            if settings.debug:
                self.collects = random.choice(range(0, settings.max_score))
            self.status = "live"
            self.duration = -1
            self.completionTime = "HH:MM:SS"
            self.finishTimeAbsolute = None
        else:
            self.collects = state_data['score']
            self.status = state_data['status']
            self.duration = state_data['duration']
            self.completionTime = state_data['duration-str']
            self.finishTimeAbsolute = None
            if state_data['finishtime'] != '':
                self.finishTimeAbsolute = datetime.datetime.fromisoformat(state_data['finishtime'])
        
        try:
            self.profile = pygame.image.load(os.path.join(settings.baseDir,f"profiles/{self.name}.png"))
        except pygame.error:
            self.profile = pygame.image.load(os.path.join(settings.baseDir,"resources/error.png"))

    def update(self, count):
        if self.status == "live":
            if 0 <= count < settings.max_score:
                self.collects = count
                return self.nameCaseSensitive + mode.hasCollected(self.collects) + " (Place: #" + str(self.place) + ")"
            elif count == settings.max_score:
                self.collects = count
                self.finish()
                return self.nameCaseSensitive + " has finished!"
        return ""
    
    #add startTime + duration to calculate new finish time
    def manualDuration(self, startTime):               
        self.finishTimeAbsolute = startTime + datetime.timedelta(seconds=self.duration)

    def calculateCompletionTime(self, startTime):
        if type(self.finishTimeAbsolute) != datetime.datetime:
            return
        self.duration = (self.finishTimeAbsolute - startTime).total_seconds()

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
        self.completionTime = finishTime

    def finish(self):
        self.finishTimeAbsolute = datetime.datetime.now()
        self.calculateCompletionTime(settings.startTime)
        self.status = "done"

    def fail(self, status):
        self.finishTimeAbsolute = datetime.datetime.now()
        self.calculateCompletionTime(settings.startTime)
        self.status = status
    
    def backup(self):
        p = {}
        p['score'] = self.collects
        p['status'] = self.status
        p['duration'] = self.duration
        p['duration-str'] = self.completionTime
        if type(self.finishTimeAbsolute) == datetime.datetime:
            p['finishtime'] = self.finishTimeAbsolute.isoformat().split(".")[0]
        else:
            p['finishtime'] = ""
        
        with open(os.path.join(settings.baseDir,'backup.json'), 'r+') as f:
            j = json.load(f)
            j[self.name] = p
            f.seek(0)
            json.dump(j, f, indent=4)
            f.truncate()
