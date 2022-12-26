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

recon = False

def fetchIRC(thisChat, playerLookup):
    global recon
    while True:
        try:
            if recon:
                recon = False
                thisChat.reconnect()
                time.sleep(1)
            readbuffer = thisChat.currentSocket.recv(4096).decode("UTF-8", errors = "ignore")
            if readbuffer == "": #reconnect on server disconnect
                print(datetime.datetime.now().isoformat().split(".")[0], "Empty readbuffer")
                recon = True
                continue
            lines = readbuffer.split("\n")
            for line in lines:
                process_line(line, thisChat, playerLookup)
        except UnicodeEncodeError:
            print(datetime.datetime.now().isoformat().split(".")[0], "UnicodeEncodeError (emoji or other non-ascii character encountered. fix?)")
            recon = True
        except ConnectionResetError:
            print(datetime.datetime.now().isoformat().split(".")[0], "ConnectionResetError")
            recon = True
        except ConnectionAbortedError:
            print(datetime.datetime.now().isoformat().split(".")[0], "ConnectionAbortedError")
            recon = True
        except TimeoutError:
            print(datetime.datetime.now().isoformat().split(".")[0], "TimeoutError")
            recon = True
        except Exception:
            print(datetime.datetime.now().isoformat().split(".")[0], "Unexpected error")
            print(traceback.format_exc())
            recon = True

def process_line(line, currentChat, playerLookup):
    global recon
    if line == "":
        return
    line = line.rstrip().split()
    # i don't know why line is sometimes (rarely) empty here
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

    user = ""
    command = []
    channel = ""
    whisper = False
    for index, word in enumerate(line):
        if index == 0:
            user = word.split('!')[0]
            #user = user[0:24] # what's this for?
            if user == "PING":
                currentChat.pong()
                return
            if len(line) < 4:
                return
        if index == 2:
            # if line[1] == "WHISPER":
            #     whisper = True
            #     channel = "#"+user
            #     continue
            channel = word
        if index == 3:
            if len(word) <= 1:
                return
            command.append(word.lower()[1:])
        if index >= 4:
            command.append(word)
    
    if len(channel) <= 1:
        channel = "00-main"
    if channel[0] != "#":
        channel = "00-main"
    path = f"irc/{channel[1:]}.log"
    
    #filter out non-ascii text to prevent UnicodeEncodeError on write() call
    full_line = " "
    for word in line:
        full_line += "".join(c if ord(c)<128 else "." for c in word) + " "
    full_line = full_line[0:-1]
    with open(os.path.join(settings.baseDir,path), 'a') as f:
        f.write(datetime.datetime.now().isoformat().split(".")[0] + full_line + "\n")
    
    user = user.lower()[1:]

    if len(command) < 1:
        return
    if command[0][0] != '!':
        return
    if command[0] in ['!ping','!roles','!racecommands','!whitelist','!unwhitelist','!add','!set','!rejoin','!quit','!start','!forcequit','!dq','!noshow', '!revive', '!settime', '!blacklist', '!unblacklist', '!admin', '!debugquit', '!togglestream', '!restart', "!fetchracers"]:
        print("[In chat "+channel+"] "+user+":"+str(command))

    # global commands
    if command[0] == "!ping":
        if whisper:
            currentChat.message(channel, "/w "+user+" Hi. Bot is alive.")
        currentChat.message(channel, "Hi. Bot is alive.")
    if command[0] == "!racecommands":
        currentChat.message(channel, "Multimario race bot command list: https://pastebin.com/d7mPZd13")
    if command[0] == "!roles":
        if len(command) == 1:
            statusMsg = users.roles(user, playerLookup)
        else:
            statusMsg = users.roles(command[1], playerLookup)
        if statusMsg is not None:
            currentChat.message(channel, statusMsg)

    # shared commands
    if (user in users.admins) or (user in playerLookup.keys()):
        if command[0] == "!whitelist" and len(command) == 2:
            subject = command[1].lower()
            if subject in users.blacklist:
                currentChat.message(channel, "Sorry, {0} is on the blacklist.".format(command[1]))
            elif subject not in users.updaters:
                if users.add(subject,users.Role.UPDATER):
                    currentChat.message(channel, command[1] + " is now an updater.")
                else:
                    currentChat.message(channel, "Twitch username {0} not found.".format(command[1]))
            else:
                currentChat.message(channel, command[1] + " is already an updater.")
        if command[0] == "!unwhitelist" and len(command) == 2:
            subject = command[1].lower()
            if subject in users.updaters:
                users.remove(subject,users.Role.UPDATER)
                currentChat.message(channel, command[1] + " is no longer an updater.")
            else:
                currentChat.message(channel, command[1] + " is already not an updater.")

    # racer commands
    if user in playerLookup.keys():
        if command[0] in ["!rejoin", "!unquit"]:
            if playerLookup[user].status == "quit":
                playerLookup[user].status = "live"
                currentChat.message(channel, playerLookup[user].nameCaseSensitive +" has rejoined the race.")
            elif playerLookup[user].status == "done":
                playerLookup[user].score -= 1
                playerLookup[user].status = "live"
                currentChat.message(channel, playerLookup[user].nameCaseSensitive +" has rejoined the race.")
            settings.redraw = True
        
        if command[0] == "!quit" and playerLookup[user].status == "live":
            playerLookup[user].finish("quit")
            settings.redraw = True
            currentChat.message(channel, playerLookup[user].nameCaseSensitive + " has quit.")

    #!add/!set
    if command[0] in ["!add","!set"]:
        if ((user not in users.updaters) and (not ismod_orvip) and (user not in playerLookup.keys())) or (user in users.blacklist):
            currentChat.message(channel, user+": You do not have permission to update score counts.")
            return

        if len(command) == 3:
            racer = command[1].lower()
            number = command[2]
        elif len(command) == 2 and user in playerLookup.keys():
            racer = user.lower()
            number = command[1]
        else:
            return

        try:
            number = int(number)
        except ValueError:
            currentChat.message(channel, user+": Not a number.")
            return
        if racer not in playerLookup.keys():
            currentChat.message(channel, user+": Racer not found.")
            return
        response = ""
        if command[0] == "!add":
            response = playerLookup[racer].update(playerLookup[racer].score + number, playerLookup)
        elif command[0] == "!set":
            response = playerLookup[racer].update(number, playerLookup)
        
        # Log score update in external file
        users.log(userId, userCS, playerLookup[racer].nameCaseSensitive)

        if response != "":
            currentChat.message(channel, response)
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
                # only subtract 1 if the racer was done at time of issued command.
                if playerLookup[racer].status == "done":
                    playerLookup[racer].score -= 1
                playerLookup[racer].status = "live"
                # if the player had max_score while quit/dqed, set status to done.
                if playerLookup[racer].score == settings.max_score:
                    playerLookup[racer].status = "done"
                settings.redraw = True
                currentChat.message(channel, playerLookup[racer].nameCaseSensitive + " has been revived.")
        elif command[0] == "!settime" and len(command) == 3:
            subject = command[1].lower()
            if subject in playerLookup.keys():
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
            newRacers = gsheets.getRacers()
            new_racers_lower = []

            # add new racers from the sheet
            for r in newRacers:
                new_racers_lower.append(r.lower())
                if r.lower() not in playerLookup.keys():
                    currentChat.message(channel, "Adding new racer {0} found on the Google spreadsheet.".format(r))
                    playerLookup[r.lower()] = player.Player(r, {})
                    currentChat.channels.append(r.lower())
                    time.sleep(0.5)
            
            #delete racers that have been removed from the sheet
            p_keys = list(playerLookup.keys())
            for p in p_keys:
                if p not in new_racers_lower:
                    currentChat.message(channel, "Removing racer {0} not found on the Google spreadsheet.".format(playerLookup[p].nameCaseSensitive))
                    playerLookup.pop(p)
                    time.sleep(0.5)

            # tell the loop to reconnect to chat with new channel(s)
            recon = True
            # and trigger a sort and redraw to remove old player cards
            settings.redraw = True
