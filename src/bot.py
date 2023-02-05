import datetime
import os
import json
import traceback
import time
from pynput.keyboard import Key, Controller
import users
import settings
import gsheets
import player
import chatroom

def init(playerLookup):
    channels = []
    for c in settings.extra_chats:
        if c.lower() not in playerLookup.keys():
            channels.append(c.lower())
    for c in playerLookup.keys():
        channels.append(c)
    chat = chatroom.ChatRoom(channels)
    while True:
        try:
            readbuffer = chat.recv()
            for line in readbuffer:
                process_line(line, chat, playerLookup)
        except Exception:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Error in bot: {traceback.format_exc()}")

def process_line(line, currentChat, playerLookup):
    if "PING :tmi.twitch.tv" in line:
        currentChat.pong(line.replace('PING', 'PONG'))
    line = line.strip().split()
    if len(line) == 0:
        return

    # Twitch message tag processing
    ismod_orvip = False
    userId = ""
    userCS = ""
    if line[0][0] == "@":
        tags = line.pop(0)
        tmp = tags.split("mod=")
        if len(tmp) > 1 and len(tmp[1])> 0 and tmp[1][0] == "1":
            ismod_orvip = True
        tmp = tags.split("vip=")
        if len(tmp) > 1 and len(tmp[1])> 0 and tmp[1][0] == "1":
            ismod_orvip = True
        tmp = tags.split("user-id=")
        if len(tmp) > 1:
            userId = tmp[1].split(";")[0]
        tmp = tags.split("display-name=")
        if len(tmp) > 1:
            userCS = tmp[1].split(";")[0]

    if len(line) < 4:
        return
    command = []
    whisper = False
    user = line[0].split('!')[0].lower()[1:]
    channel = line[2]
    command.append(line[3].lower()[1:])
    for index, word in enumerate(line):
        if index >= 4:
            command.append(word)
    # filters out messages with 3-number tags (e.g. not PRIVMSG)
    if len(line[1]) == 3:
        return

    if len(channel) < 1 or channel[0] != "#":
        channel = "#0-main"
    path = f"irc/{channel[1:]}.log"
    full_line = " "
    #filter out non-ascii text to prevent UnicodeEncodeError on write() call
    for word in line:
        full_line += "".join(c if ord(c)<128 else "." for c in word) + " "
    with open(os.path.join(settings.baseDir,path), 'a+') as f:
        f.write(datetime.datetime.now().isoformat().split(".")[0] + full_line[0:-1] + "\n")

    if userId == "":
        return
    if len(command) < 1 or len(command[0]) < 1 or command[0][0] != '!':
        return
    if command[0] in ['!ping','!roles','!mmstatus','!racecommands','!whitelist','!unwhitelist','!add','!set','!rejoin','!quit','!start','!forcequit','!dq','!noshow', '!revive', '!settime', '!blacklist', '!unblacklist', '!admin', '!debugquit', '!togglestream', '!restart', "!fetchracers", "!mmleave","!mmjoin","!clearstats"]:
        st = settings.startTime.isoformat().split("T")[0]
        with open(os.path.join(settings.baseDir,f"log/{st}.txt"), 'a+') as f:
            f.write(f"{datetime.datetime.now().isoformat().split('.')[0]} [{channel}] {user}: {' '.join(command)}\n")

    # global commands
    if command[0] == "!ping":
        if whisper:
            currentChat.message(channel, "/w "+user+" Hi. Bot is alive.")
        currentChat.message(channel, "Hi. Bot is alive.")
    if command[0] == "!racecommands":
        currentChat.message(channel, "Multimario race bot command list: https://pastebin.com/d7mPZd13")
    if command[0] in ["!roles","!mmstatus"]:
        if len(command) == 1:
            statusMsg = users.roles(user, playerLookup)
        else:
            statusMsg = users.roles(command[1], playerLookup)
        currentChat.message(channel, statusMsg)

    # shared commands
    if (user in users.admins) or (user in playerLookup.keys()):
        if command[0] == "!whitelist" and len(command) == 2:
            subject = command[1].lower()
            if subject in users.blacklist:
                currentChat.message(channel, f"Sorry, {command[1]} is on the blacklist.")
            elif subject not in users.updaters:
                if users.add(subject,users.Role.UPDATER):
                    currentChat.message(channel, f"{command[1]} is now an updater.")
                else:
                    currentChat.message(channel, f"Twitch username {command[1]} not found.")
            else:
                currentChat.message(channel, f"{command[1]} is already an updater.")
        if command[0] == "!unwhitelist" and len(command) == 2:
            subject = command[1].lower()
            if subject in users.updaters:
                users.remove(subject,users.Role.UPDATER)
                currentChat.message(channel, f"{command[1]} is no longer an updater.")
            else:
                currentChat.message(channel, f"{command[1]} is already not an updater.")
    
    if command[0] == "!mmleave":
        l_channel = ""
        if len(command) == 1:
            if user != channel[1:]:
                return
            l_channel = channel[1:]
        elif len(command) == 2:
            if user not in users.admins:
                return
            l_channel = command[1].lower()
        else:
            return
        if l_channel not in currentChat.channels:
            currentChat.message(channel,f"{userCS}: Already not active in channel #{l_channel}.")
            return
        currentChat.message(channel,f"{userCS}: Leaving #{l_channel} now.")
        currentChat.part(l_channel)
    
    if command[0] == "!mmjoin":
        j_channel = ""
        if len(command) == 1:
            if user not in playerLookup.keys():
                return
            j_channel = user
        elif len(command) == 2:
            if user not in users.admins:
                return
            j_channel = command[1].lower()
        else:
            return
        if j_channel in currentChat.channels:
            currentChat.message(channel,f"{userCS}: Rejoining #{j_channel} now.")
            currentChat.part(j_channel)
            currentChat.join(j_channel)
            return
        currentChat.message(channel,f"{userCS}: Joining #{j_channel} now.")
        currentChat.join(j_channel)

    # racer commands
    if user in playerLookup.keys():
        if command[0] in ["!rejoin", "!unquit"]:
            if playerLookup[user].status != "quit":
                return
            playerLookup[user].status = "live"
            if playerLookup[user].score == settings.max_score:
                playerLookup[user].status = "done"
            currentChat.message(channel, playerLookup[user].nameCaseSensitive +" has rejoined the race.")
            settings.redraw = True
        
        if command[0] == "!quit" and playerLookup[user].status == "live":
            playerLookup[user].finish("quit")
            settings.redraw = True
            currentChat.message(channel, playerLookup[user].nameCaseSensitive + " has quit.")

    #!add/!set
    if command[0] in ["!add","!set"]:
        if ((user not in users.updaters) and (not ismod_orvip) and (user not in playerLookup.keys())) or (user in users.blacklist):
            currentChat.message(channel, f"{userCS}: You do not have permission to update score counts.")
            return

        if len(command) == 3:
            racer = command[1].lower()
            number = command[2]
        elif len(command) == 2 and user in playerLookup.keys():
            racer = user.lower()
            number = command[1]
        else:
            return

        if racer not in playerLookup.keys():
            currentChat.message(channel, f"{userCS}: Racer {racer} not found.")
            return
        p = playerLookup[racer]
        try:
            number = int(number)
        except ValueError:
            currentChat.message(channel, f"{userCS}: Not a number.")
            return
        
        if command[0] == "!add" and number == 0:
            currentChat.message(channel, "Use !mmstatus [username] to check a racer's current status.")
            return

        response = ""
        if command[0] == "!add":
            number += p.score

        if p.status not in ["live","done"]:
            currentChat.message(channel, f"{p.nameCaseSensitive} is not live, so their score cannot be updated.")
            return
        if number < 0 or number > settings.max_score:
            currentChat.message(channel, "The requested score is less than 0 or greater than the maximum possible score.")
            return
        
        response = p.update(number, playerLookup)
        currentChat.message(channel, response)
        # Log score update in external file
        users.log(userId, userCS, p.nameCaseSensitive)
        settings.redraw = True

    # admin commands
    if user in users.admins:
        if command[0] == "!start":
            newTime = -1
            if len(command)==1:
                newTime = datetime.datetime.now()
            elif len(command)==2:
                newTime = command[1]
                try:
                    newTime = datetime.datetime.fromisoformat(newTime)
                except ValueError:
                    currentChat.message(channel, "Invalid date format. Must be of this format: 2018-12-29@09:00")
            else:
                currentChat.message(channel, "Invalid date format. Must be of this format: 2018-12-29@09:00")
            if type(newTime) == datetime.datetime:
                settings.startTime = newTime
                with open(os.path.join(settings.baseDir,'settings.json'), 'r+') as f:
                    j = json.load(f)
                    j['start-time'] = settings.startTime.isoformat().split(".")[0]
                    f.seek(0)
                    json.dump(j, f, indent=4)
                    f.truncate()
                currentChat.message(channel, "The race start time has been set to " + settings.startTime.isoformat().split(".")[0])
                for racer in playerLookup.keys():
                    playerLookup[racer].calculateDuration()
                settings.redraw = True
        elif command[0] == "!forcequit" and len(command) == 2:
            racer = command[1].lower()
            if racer in playerLookup.keys():
                if playerLookup[racer].status == "live" or playerLookup[racer].status == "done":
                    playerLookup[racer].finish("quit")
                    settings.redraw = True
                    currentChat.message(channel, playerLookup[racer].nameCaseSensitive + " has been forcequit.")
        elif command[0] == "!noshow" and len(command) == 2:
            racer = command[1].lower()
            if racer in playerLookup.keys():
                playerLookup[racer].finish("noshow")
                settings.redraw = True
                currentChat.message(channel, playerLookup[racer].nameCaseSensitive + " set to No-show.")
        elif command[0] == "!dq" and len(command) == 2:
            racer = command[1].lower()
            if racer in playerLookup.keys():
                if playerLookup[racer].status == "live" or playerLookup[racer].status == "done":
                    playerLookup[racer].finish("disqualified")
                    settings.redraw = True
                    currentChat.message(channel, playerLookup[racer].nameCaseSensitive + " has been disqualified.")
        elif command[0] == "!revive" and len(command) == 2:
            racer = command[1].lower()
            if racer in playerLookup.keys():
                playerLookup[racer].status = "live"
                if playerLookup[racer].score == settings.max_score:
                    playerLookup[racer].status = "done"
                settings.redraw = True
                currentChat.message(channel, playerLookup[racer].nameCaseSensitive + " has been revived.")
        elif command[0] == "!settime" and len(command) == 3:
            subject = command[1].lower()
            if subject not in playerLookup.keys():
                currentChat.message(channel, f"Racer {subject} not found.")
            racer = playerLookup[subject]
            newTime = command[2].split(":")
            if len(newTime) != 3:
                currentChat.message(channel, "Invalid time string.")
                return
            try:
                duration = int(newTime[2]) + 60*int(newTime[1]) + 3600*int(newTime[0])
            except ValueError:
                currentChat.message(channel, "Invalid time string.")
                return
            if int(newTime[1]) >= 60 or int(newTime[2]) >= 60:
                currentChat.message(channel, "Invalid time string.")
                return
            
            racer.finishTimeAbsolute = settings.startTime + datetime.timedelta(seconds=duration)
            racer.calculateDuration()

            settings.redraw = True
            currentChat.message(channel, racer.nameCaseSensitive+"'s time has been updated.")
        elif command[0] == "!blacklist" and len(command) == 2:
            subject = command[1].lower()
            if subject not in users.blacklist:
                users.add(subject,users.Role.BLACKLIST)
                if subject in users.updaters:
                    users.remove(subject,users.Role.UPDATER)
                currentChat.message(channel, command[1] + " has been blacklisted.")
            else:
                currentChat.message(channel, command[1] + " is already blacklisted.")
        elif command[0] == "!unblacklist" and len(command) == 2:
            subject = command[1].lower()
            if subject in users.blacklist:
                users.remove(subject,users.Role.BLACKLIST)
                currentChat.message(channel, command[1] + " is no longer blacklisted.")
            else:
                currentChat.message(channel, command[1] + " is already not blacklisted.")
        elif command[0] == "!admin" and len(command) == 2:
            subject = command[1].lower()
            if subject not in users.admins:
                users.add(subject,users.Role.ADMIN)
                currentChat.message(channel, command[1] + " is now an admin.")
            else:
                currentChat.message(channel, command[1] + " is already an admin.")
        elif command[0] == "!debugquit":
            currentChat.message(channel, "Quitting program.")
            settings.doQuit = True
        elif command[0] == "!togglestream":
            kb = Controller()
            with kb.pressed(Key.ctrl):
                kb.tap("5")
            currentChat.message(channel, "Toggled stream.")
        elif command[0] == "!fetchracers":
            settings.playersLock = True
            newRacers = gsheets.getRacers()
            new_racers_lower = []
            no_change = True

            # add new racers from the sheet
            for r in newRacers:
                new_racers_lower.append(r.lower())
                if r.lower() not in playerLookup.keys():
                    no_change = False
                    currentChat.message(channel, f"Adding new racer {r} found on the Google spreadsheet.")
                    playerLookup[r.lower()] = player.Player(r, {})
                    time.sleep(0.5)
                    currentChat.join(r.lower())

            #delete racers that have been removed from the sheet
            p_keys = list(playerLookup.keys())
            for r in p_keys:
                if r not in new_racers_lower:
                    no_change = False
                    currentChat.message(channel, f"Removing racer {playerLookup[r].nameCaseSensitive} not found on the Google spreadsheet.")
                    playerLookup.pop(r)
                    time.sleep(0.5)
                    currentChat.part(r)

            if no_change:
                currentChat.message(channel, f"No changes were found between the bot's player list and Google Sheets.")
                
            settings.playersLock = False
            # and trigger a sort and redraw to remove old player cards
            settings.redraw = True
        elif command[0] == "!clearstats":
            for p in playerLookup.keys():
                playerLookup[p].score = 0
                playerLookup[p].status = "live"
            currentChat.message(channel, f"{userCS}: Cleared all racer stats.")
            settings.redraw = True
