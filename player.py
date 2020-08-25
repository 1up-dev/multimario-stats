import random
import pygame
import time
import datetime
import math
import chatroom
import json

class Player:
    def __init__(self, name, NICK, PASSWORD, debug):
        self.name = name.lower()
        self.nameCaseSensitive = name
        self.corner = (0,0)
        self.collects = 0
        if debug:
            self.collects = random.choice(range(0,602))
        self.status = "live"
        self.place = 1
        self.duration = -1
        self.completionTime = "HH:MM:SS"
        self.finishTimeAbsolute = None
        try:
            self.profile = pygame.transform.scale(pygame.image.load("./profiles/{0}.png".format(name)), (60,60))
        except pygame.error:
            self.profile = pygame.transform.scale(pygame.image.load("./resources/error.png"), (60,60))
        time.sleep(1)
        self.chat = chatroom.ChatRoom("#"+self.name, NICK, PASSWORD)

    def update(self, count):
        if self.status == "live":
            if 0 <= count < 602:
                self.collects = count
                return self.hasCollected()
            elif count == 602:
                self.collects = count
                self.finish(self.getStartTime())
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
            pass
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

    def finish(self, startTime):
        self.finishTimeAbsolute = datetime.datetime.now()
        self.calculateCompletionTime(startTime)
        self.status = "done"

    def fail(self, status, startTime):
        self.finishTimeAbsolute = datetime.datetime.now()
        self.calculateCompletionTime(startTime)
        self.status = status

    def getStartTime(self):
        with open('settings.json','r') as f:
            j = json.load(f)
            raw_time = j['start-time']
            return datetime.datetime.fromisoformat(raw_time)

    def hasCollected(self):
        tempStars = self.collects
        game=""
        buffer=""
        noun="Star"
        if tempStars <= 120:
            game="Super Mario 64"
        elif tempStars <= 240:
            game="Super Mario Galaxy"
            tempStars -= 120
        elif tempStars <= 360:
            game="Super Mario Sunshine"
            tempStars -= 240
            noun="Shine"
        elif tempStars <= 602:
            game="Super Mario Galaxy 2"
            tempStars -= 360
        if tempStars != 1:
            buffer = "s"
        return self.nameCaseSensitive + " now has " + str(tempStars) + " "+ noun+buffer + " in " + game + "."
