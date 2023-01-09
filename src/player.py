import random
import os
import datetime
import math
import json
import settings
import sort
import twitch

class Player:
    def __init__(self, name, state_data):
        self.name = name.lower()
        self.nameCaseSensitive = name
        self.corner = (0,0)
        self.place = 1
        self.score = 0
        self.duration_str = ""
        self.duration = 0
        self.finishTimeAbsolute = None
        self.status = "live"
        self.profile = twitch.fetchProfile(self.name)
        if state_data == {} and settings.debug:
            self.score = random.choice(range(0, settings.max_score))
        if state_data != {}:
            self.score = state_data['score']
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
            collectible += "s"
        return (score, collectible, game)

    def update(self, count, playerLookup):
        if self.status not in ["live","done"]:
            return
        if count < 0 or count > settings.max_score:
            return
        
        if 0 <= count < settings.max_score:
            if self.status == "done":
                #if updating a done racer, set them to live
                self.status = "live"
            self.score = count
            # sort() reassigns place numbers so the command output will be accurate
            sort.sort(playerLookup)
            score, collectible, game = self.collected()
            return f"{self.nameCaseSensitive} now has {str(score)} {collectible} in {game}. (Place: #{str(self.place)})"
        elif count == settings.max_score:
            self.score = count
            self.finish("done")
            sort.sort(playerLookup)
            return f"{self.nameCaseSensitive} has finished in place #{self.place} with a time of {self.duration_str}! GG!"

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
        
        delete_backup = False
        with open(os.path.join(settings.baseDir,'backup.json'), 'r+') as f:
            try:
                j = json.load(f)
                j[self.name] = p
                f.seek(0)
                json.dump(j, f, indent=4)
                f.truncate()
            except json.decoder.JSONDecodeError:
                print("Error: Backup failed to load. Clearing it")
                delete_backup = True
        if delete_backup:
            with open(os.path.join(settings.baseDir,'backup.json'), 'w') as f:
                json.dump({}, f, indent=4)

def backup_all(players):
    p = {}
    for player in players:
        pl = players[player]
        p[pl.name] = {}
        p[pl.name]['score'] = pl.score
        p[pl.name]['status'] = pl.status
        if pl.finishTimeAbsolute == None:
            p[pl.name]['finishtime'] = None
        else:
            p[pl.name]['finishtime'] = pl.finishTimeAbsolute.isoformat()
    with open(os.path.join(settings.baseDir,'backup.json'), 'w') as f:
        json.dump(p, f, indent=4)
