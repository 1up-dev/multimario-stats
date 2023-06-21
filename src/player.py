import random
import os
import datetime
import json
import settings
import sort
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
            collectible += "s"
        return (score, collectible, game)

    def update(self, count, playerLookup):
        if self.status not in ["live","done"]:
            return
        if count < 0 or count > settings.max_score:
            return
        
        self.score = count
        # sort() reassigns place numbers so the command output will be accurate
        sort.sort(playerLookup)

        if 0 <= count < settings.max_score:
            if self.status == "done":
                self.status = "live"
            score, collectible, game = self.collected()
            return f"{self.display_name} now has {str(score)} {collectible} in {game}. (Place #{str(self.place)}, Score {self.score})"
        elif count == settings.max_score:
            self.finish("done")
            twitch.create_clip_async(self.twitch_id, self.name)
            return f"{self.display_name} has finished in place #{self.place} with a time of {self.duration_str}! GG!"

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
    
    def backup(self):
        p = {}
        p['score'] = self.score
        p['status'] = self.status
        if self.finishTimeAbsolute == None:
            p['finishtime'] = None
        else:
            p['finishtime'] = self.finishTimeAbsolute.isoformat()
        
        delete_backup = False
        with open(settings.path('backup.json'), 'r+') as f:
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
            with open(settings.path('backup.json'), 'w') as f:
                json.dump({}, f, indent=4)

def backup_all(players):
    with open(settings.path('backup.json'), 'r+') as f:
        j = json.load(f)
        for p in players:
            player = players[p]
            j[player.name] = {}
            j[player.name]['score'] = player.score
            j[player.name]['status'] = player.status
            j[player.name]['finishtime'] = None
            if player.finishTimeAbsolute != None:
                j[player.name]['finishtime'] = player.finishTimeAbsolute.isoformat().split(".")[0]
        f.seek(0)
        json.dump(j, f, indent=4)
        f.truncate()
