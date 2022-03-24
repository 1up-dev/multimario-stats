import datetime
import os
import sys
import json
import traceback
import time
#import pyautogui
from pynput.keyboard import Key, Controller
import users
import settings

def fetchIRC(thisChat, playerLookup):
    recon = False
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
        except ConnectionResetError:
            print(datetime.datetime.now().isoformat().split(".")[0], "ConnectionResetError")
            recon = True
        except TimeoutError:
            print(datetime.datetime.now().isoformat().split(".")[0], "TimeoutError")
            recon = True
        except Exception:
            print(datetime.datetime.now().isoformat().split(".")[0], "Unexpected error")
            print(traceback.format_exc())
            recon = True

def process_line(line, currentChat, playerLookup):
    if line == "":
        return
    #print(line)
    line = line.rstrip().split()
    if len(line) == 0:
        print("this condition is necessary")
        return

    ismod = False
    userId = -1
    if line[0][0] == "@":
        tags = line.pop(0)
        tmp8 = tags.split("mod=")
        if len(tmp8) > 1:
            if tmp8[1][0] == "1":
                ismod = True
        tmp9 = tags.split("user-id=")
        if len(tmp9) > 1:
            userId = tmp9[1].split(";")[0]

    user = ""
    command = []
    channel = ""
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
    with open(os.path.join(settings.baseDir,path), 'a') as f:
        f.write(datetime.datetime.now().isoformat().split(".")[0] + " " + " ".join(line) + "\n")
    
    #print("[user]", user, "[command]", command, "[userid]", userid, "[ismod]", ismod)
    
    if len(command) < 1:
        print("error: command is empty.",)
        return
    
    if command[0] not in ['!ping','!roles','!racecommands','!whitelist','!unwhitelist','!add','!set','!rejoin','!quit','!start','!forcequit','!dq','!noshow', '!revive', '!settime', '!blacklist', '!unblacklist', '!admin', '!debugquit', '!togglestream', '!restart']:
        return
    user = user.lower()[1:]
    print("[In chat "+channel+"] "+user+":"+str(command))

    # global commands
    if command[0] == "!ping":
        currentChat.message(channel, "Hi. Bot is alive.")
    if command[0] == "!racecommands":
        currentChat.message(channel, "Command list: https://pastebin.com/d7mPZd13")
    if command[0] == "!roles":
        if len(command) == 1:
            statusMsg = users.status(user, playerLookup)
        else:
            statusMsg = users.status(command[1], playerLookup)
        if statusMsg is not None:
            currentChat.message(channel, statusMsg)

    # shared commands
    if (user in users.admins) or (user in users.racersL):
        if command[0] == "!whitelist" and len(command) == 2:
            subject = command[1].lower()
            if subject in users.blacklist:
                currentChat.message(channel, "Sorry, " + command[1] + " is on the blacklist.")
            elif subject not in users.updaters:
                if users.add(subject,users.Role.UPDATER):
                    currentChat.message(channel, command[1] + " is now an updater.")
                else:
                    currentChat.message(channel, "Twitch username {0} not found: ".format(command[1]))
            else:
                currentChat.message(channel, command[1] + " is already an updater.")
        elif command[0] == "!unwhitelist" and len(command) == 2:
            subject = command[1].lower()
            if subject in users.updaters:
                users.remove(subject,users.Role.UPDATER)
                currentChat.message(channel, command[1] + " is no longer an updater.")
            else:
                currentChat.message(channel, command[1] + " is already not an updater.")

    # racer commands
    if user in users.racersL:
        if (command[0] == "!add" or command[0] == "!set") and len(command) == 2:
            try:
                number = int(command[1])
                if user in playerLookup.keys():
                    response = ""
                    if command[0] == "!add":
                        response = playerLookup[user].update(playerLookup[user].collects + number)
                    elif command[0] == "!set":
                        response = playerLookup[user].update(number)
                    if response != "":
                        currentChat.message(channel, response)
                    settings.redraw = True
            except ValueError:
                pass
        
        if (command[0] == "!rejoin"):
            if playerLookup[user].status == "quit":
                playerLookup[user].status = "live"
                currentChat.message(channel, playerLookup[user].nameCaseSensitive +" has rejoined the race.")
            elif playerLookup[user].status == "done":
                playerLookup[user].collects -= 1
                playerLookup[user].status = "live"
                currentChat.message(channel, playerLookup[user].nameCaseSensitive +" has rejoined the race.")
            settings.redraw = True
        
        if command[0] == "!quit" and playerLookup[user].status == "live":
            playerLookup[user].fail("quit")
            settings.redraw = True
            currentChat.message(channel, playerLookup[user].nameCaseSensitive + " has quit.")

    # updater commands
    if ((user in users.updaters) or (ismod==True) or (user in users.racersL)) and (user not in users.blacklist):
        if (command[0] == "!add" or command[0] == "!set") and len(command) == 3:
            player = command[1].lower()
            try:
                number = int(command[2])
                if player in playerLookup.keys():
                    response = ""
                    if command[0] == "!add":
                        response = playerLookup[player].update(playerLookup[player].collects + number)
                    elif command[0] == "!set":
                        response = playerLookup[player].update(number)
                    if response != "":
                        currentChat.message(channel, response)
                    settings.redraw = True
            except ValueError:
                pass

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
                for player in playerLookup.keys():
                    playerLookup[player].calculateCompletionTime(settings.startTime)
                settings.redraw = True
        elif command[0] == "!forcequit" and len(command) == 2:
            player = command[1].lower()
            if player in playerLookup.keys():
                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                    playerLookup[player].fail("quit")
                    settings.redraw = True
                    currentChat.message(channel, command[1] + " has been forcequit.")
        elif command[0] == "!noshow" and len(command) == 2:
            player = command[1].lower()
            if player in playerLookup.keys():
                playerLookup[player].fail("noshow")
                settings.redraw = True
                currentChat.message(channel, command[1] + " set to No-show.")
        elif command[0] == "!dq" and len(command) == 2:
            player = command[1].lower()
            if player in playerLookup.keys():
                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                    playerLookup[player].fail("disqualified")
                    settings.redraw = True
                    currentChat.message(channel, command[1] + " has been disqualified.")
        elif command[0] == "!revive" and len(command) == 2:
            player = command[1].lower()
            if player in playerLookup.keys():
                if playerLookup[player].status == "done":
                    playerLookup[player].collects -= 1
                playerLookup[player].status = "live"
                if playerLookup[player].collects == settings.max_score:
                    playerLookup[player].status = "done"
                settings.redraw = True
                currentChat.message(channel, command[1] + " has been revived.")
        elif command[0] == "!settime" and len(command) == 3:
            subject = command[1].lower()
            if subject in playerLookup.keys():
                player = playerLookup[subject]
                stringTime = command[2]
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
                
                player.duration = duration
                player.completionTime = stringTime
                player.manualDuration(settings.startTime)
                settings.redraw = True
                currentChat.message(channel, player.nameCaseSensitive+"'s time has been updated.")
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
            #pyautogui.hotkey("ctrl","5")
            kb = Controller()
            with kb.pressed(Key.ctrl):
                kb.tap("5")
            currentChat.message(channel, "Toggled stream.")
        # elif command[0] == '!restart':
        #     currentChat.message(channel, "Restarting...")
        #     os.execv(sys.executable, ["python"] + sys.argv)
