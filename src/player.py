import random
import pygame
import time
import datetime
import math
import chatroom
import json
import mode_602
import mode_1120
import mode_246

class Player:
    def __init__(self, name, NICK, PASSWORD, debug, mode, state_data):
        self.name = name.lower()
        self.nameCaseSensitive = name
        self.corner = (0,0)
        self.place = 1
        self.mode = int(mode)
        if state_data == {}:
            self.collects = 0
            if debug:
                self.collects = random.choice(range(0,self.mode))
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
            self.profile = pygame.image.load(f"./profiles/{self.name}.png")
        except pygame.error:
            self.profile = pygame.image.load("./resources/error.png")
        
        self.chat = chatroom.ChatRoom(self.name, NICK, PASSWORD)

    def update(self, count):
        if self.status == "live":
            if 0 <= count < self.mode:
                self.collects = count
                return self.hasCollected()
            elif count == self.mode:
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
        tmp = ""
        if self.mode == 602:
            tmp = mode_602.collected(self.collects)
        elif self.mode == 1120:
            tmp = mode_1120.collected(self.collects)
        if self.mode == 246:
            tmp = mode_246.collected(self.collects)
        return self.nameCaseSensitive + tmp + " (Place: #" + str(self.place) + ")"
    
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
        
        with open('backup.json', 'r+') as f:
            j = json.load(f)
            j[self.name] = p
            f.seek(0)
            json.dump(j, f, indent=4)
            f.truncate()
