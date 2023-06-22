import datetime
import json
import traceback
import users
import settings
import gsheets
import player
import chatroom
import obs
import twitch

def init(playerLookup):
    channels = []
    for c in settings.extra_chats:
        if c.lower() not in playerLookup.keys():
            channels.append(c.lower())
    for c in list(playerLookup.keys()):
        channels.append(c)
    chat = chatroom.ChatRoom(channels)
    settings.chat_ref = chat
    while True:
        if settings.doQuit:
            break
        try:
            readbuffer = chat.recv()
            for line in readbuffer:
                process_line(line, chat, playerLookup)
        except Exception:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Error in bot: {traceback.format_exc()}")

def process_line(line, currentChat, playerLookup):
    if "PING :tmi.twitch.tv" in line:
        currentChat.pong(line.replace('PING', 'PONG'))
        return
    line = line.strip().split()
    if len(line) == 0:
        return

    # Twitch message tag processing
    ismod_orvip = False
    user_id = ""
    userCS = ""
    message_id = None
    if line[0][0] == "@":
        tags = line.pop(0)[1:].split(";")
        for tag in tags:
            tag = tag.split("=")
            if len(tag) < 2:
                continue
            tag_name = tag[0]
            tag_value = tag[1]
            if tag_name == "mod" and tag_value == "1":
                ismod_orvip = True
            elif tag_name == "vip" and tag_value == "1":
                ismod_orvip = True
            elif tag_name == "user-id":
                user_id = tag_value
            elif tag_name == "display-name":
                userCS = tag_value
            elif tag_name == "id":
                message_id = tag_value

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
    with open(settings.path(path), 'a+') as f:
        f.write(datetime.datetime.now().isoformat().split(".")[0] + full_line[0:-1] + "\n")

    if user_id == "":
        return
    if len(command) < 1 or len(command[0]) < 1 or command[0][0] != '!':
        return
    if command[0] not in ["!mmcommands", "!roles","!mmstatus", "!place", "!addcounter", "!removecounter", "!mmleave", "!mmjoin", "!rejoin", "!unquit", "!quit", "!add", "!set", "!start", "!forcequit", "!noshow", "!dq", "!revive", "!settime", "!block", "!unblock", "!admin", "!mmkill", "!togglestream", "!fetchracers", "!clearstats", "!clip"]:
        return
    for i, word in enumerate(command):
        command[i] = "".join(c if ord(c)<128 else "" for c in word)
        if command[i] == "":
            del(command[i])
    
    st = settings.startTime.isoformat().split("T")[0]
    with open(settings.path(f"log/{st}-cmd.log"), 'a+') as f:
        f.write(f"{datetime.datetime.now().isoformat().split('.')[0]} [{channel}] {user}: {' '.join(command)}\n")

    # global commands
    if command[0] == "!mmcommands":
        currentChat.message(channel, "Multimario stats bot command list: https://bit.ly/44P3Y46")
    elif command[0] in ["!roles","!mmstatus"]:
        if len(command) == 1:
            statusMsg = users.roles(user, user_id, userCS, playerLookup)
        else:
            subject = command[1].lower()
            info = twitch.get_user_infos([subject])
            if info == None or len(info) == 0:
                currentChat.message(channel, f"Twitch username {subject} not found.", message_id)
                return
            info = info[0]
            subject_id = info['id']
            subject_displayname = info['display_name']
            statusMsg = users.roles(subject, subject_id, subject_displayname, playerLookup)
        currentChat.message(channel, statusMsg)
    elif command[0] == "!place":
        if len(command) < 2:
            return
        try:
            target = int(command[1])
        except ValueError:
            currentChat.message(channel, "Not a number.", message_id)
            return
        racers_in_target = []
        extra_info = ""
        for p in list(playerLookup.keys()):
            racer = playerLookup[p]
            if racer.place == target:
                racers_in_target.append(f"{racer.display_name} ({racer.status})")
                if racer.score == settings.max_score:
                    extra_info = racer.duration_str
                    break
                score, collectible, game = racer.collected()
                extra_info = f"{str(score)} {collectible} in {game}"
        if racers_in_target != []:
            currentChat.message(channel, f"#{target}: {', '.join(racers_in_target)} ({extra_info})")
            return
        currentChat.message(channel, f"Place #{target} not found (There may be a tie causing this place number to be skipped).", message_id)

    # shared commands
    elif command[0] == "!addcounter":
        if len(command) != 2:
            return
        if (user_id not in users.admins) and (user not in playerLookup.keys()):
            return
        subject = command[1].lower()
        info = twitch.get_user_infos([subject])
        if info == None or len(info) == 0:
            currentChat.message(channel, f"Twitch username {subject} not found.", message_id)
            return
        info = info[0]
        subject_id = info['id']
        subject_displayname = info['display_name']
        if subject_id in users.blocklist:
            currentChat.message(channel, f"Sorry, {subject_displayname} is blocked.")
        elif subject_id not in users.counters:
            users.add(subject, subject_id, users.Role.COUNTER)
            currentChat.message(channel, f"{subject_displayname} is now a counter.")
        else:
            currentChat.message(channel, f"{subject_displayname} is already a counter.")
    elif command[0] == "!removecounter":
        if len(command) != 2:
            return
        if (user_id not in users.admins) and (user not in playerLookup.keys()):
            return
        subject = command[1].lower()
        info = twitch.get_user_infos([subject])
        if info == None or len(info) == 0:
            currentChat.message(channel, f"Twitch username {subject} not found.", message_id)
            return
        info = info[0]
        subject_id = info['id']
        subject_displayname = info['display_name']
        if subject_id in users.counters:
            users.remove(subject_id, users.Role.COUNTER)
            currentChat.message(channel, f"{subject_displayname} is no longer a counter.")
        else:
            currentChat.message(channel, f"{subject_displayname} is already not a counter.")
    elif command[0] == "!mmleave":
        l_channel = ""
        if len(command) == 1:
            if user != channel[1:]:
                return
            l_channel = channel[1:]
        elif len(command) == 2:
            if user_id not in users.admins:
                return
            l_channel = command[1].lower()
        else:
            return
        if l_channel not in currentChat.channels:
            currentChat.message(channel,f"Already not active in channel #{l_channel}.")
            return
        currentChat.message(channel,f"Leaving #{l_channel} now.")
        currentChat.part([l_channel])
    elif command[0] == "!mmjoin":
        j_channel = ""
        if len(command) == 1:
            if user not in playerLookup.keys():
                return
            j_channel = user
        elif len(command) == 2:
            if user_id not in users.admins:
                return
            j_channel = command[1].lower()
        else:
            return
        if j_channel in currentChat.channels:
            currentChat.message(channel,f"Rejoining #{j_channel} now.")
            currentChat.part([j_channel])
            currentChat.join([j_channel])
            return
        currentChat.message(channel,f"Joining #{j_channel} now.")
        currentChat.join([j_channel])

    # racer commands
    elif command[0] in ["!rejoin", "!unquit"]:
        if user not in playerLookup.keys():
            return
        racer = playerLookup[user]
        if racer.status != "quit":
            return
        racer.status = "live"
        if racer.score == settings.max_score:
            racer.status = "done"
        currentChat.message(channel, racer.display_name +" has rejoined the race.")
        settings.redraw = True
    elif command[0] == "!quit":
        if user not in playerLookup.keys():
            return
        racer = playerLookup[user]
        if racer.status != "live":
            return
        racer.finish("quit")
        settings.redraw = True
        currentChat.message(channel, racer.display_name + " has quit.")
    elif command[0] in ["!add","!set"]:
        if ((user_id not in users.counters) and (not ismod_orvip) and (user not in playerLookup.keys())) or (user_id in users.blocklist):
            currentChat.message(channel, f"{userCS}: You do not have permission to update score counts.")
            return

        if len(command) == 3:
            racer = command[1].lower()
            number = command[2]
        elif len(command) == 2 and user in playerLookup.keys():
            racer = user
            number = command[1]
        else:
            return

        if racer not in playerLookup.keys():
            currentChat.message(channel, f"Racer {racer} not found.")
            return
        p = playerLookup[racer]
        try:
            if '+' in number:
                nums = number.split('+')
                number = 0
                for n in nums:
                    number += int(n)
            else:
                number = int(number)
        except ValueError:
            currentChat.message(channel, f"Not a number.")
            return
        
        if command[0] == "!add" and number == 0:
            currentChat.message(channel, "Use !mmstatus [username] to check a racer's current status. To check your own status, just type !mmstatus.")
            return

        response = ""
        if command[0] == "!add":
            number += p.score

        if p.status not in ["live","done"]:
            currentChat.message(channel, f"{p.display_name} is not live, so their score cannot be updated.")
            return
        if number < 0 or number > settings.max_score:
            currentChat.message(channel, "The requested score is less than 0 or greater than the maximum possible score.")
            return
        
        response = p.update(number, playerLookup)
        currentChat.message(channel, response)

        # Log score update in external file
        st = settings.startTime.isoformat().split("T")[0]
        log_file = settings.path(f"log/{st}-state.log")
        with open(log_file,'a+') as f:
            f.write(f"{datetime.datetime.now().isoformat().split('.')[0]} {p.name} {p.score} {user_id}\n")
        
        settings.redraw = True

    # admin commands
    elif user_id not in users.admins:
        return
    elif command[0] == "!start":
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
            with open(settings.path('settings.json'), 'r+') as f:
                j = json.load(f)
                j['start-time'] = settings.startTime.isoformat().split(".")[0]
                f.seek(0)
                json.dump(j, f, indent=4)
                f.truncate()
            currentChat.message(channel, "The race start time has been set to " + settings.startTime.isoformat().split(".")[0])
            for racer in list(playerLookup.keys()):
                playerLookup[racer].calculateDuration()
            settings.redraw = True
    elif command[0] == "!forcequit":
        if len(command) != 2:
            return
        racer = command[1].lower()
        if racer not in playerLookup.keys():
            return
        playerLookup[racer].finish("quit")
        settings.redraw = True
        currentChat.message(channel, playerLookup[racer].display_name + " has been forcequit.")
    elif command[0] == "!noshow":
        if len(command) != 2:
            return
        racer = command[1].lower()
        if racer not in playerLookup.keys():
            return
        playerLookup[racer].finish("noshow")
        settings.redraw = True
        currentChat.message(channel, playerLookup[racer].display_name + " set to No-show.")
    elif command[0] == "!dq":
        if len(command) != 2:
            return
        racer = command[1].lower()
        if racer not in playerLookup.keys():
            return
        playerLookup[racer].finish("disqualified")
        settings.redraw = True
        currentChat.message(channel, playerLookup[racer].display_name + " has been disqualified.")
    elif command[0] == "!revive":
        if len(command) != 2:
            return
        racer = command[1].lower()
        if racer not in playerLookup.keys():
            return
        playerLookup[racer].status = "live"
        if playerLookup[racer].score == settings.max_score:
            playerLookup[racer].status = "done"
        settings.redraw = True
        currentChat.message(channel, playerLookup[racer].display_name + " has been revived.")
    elif command[0] == "!settime":
        if len(command) != 3:
            return
        subject = command[1].lower()
        if subject not in playerLookup.keys():
            currentChat.message(channel, f"Racer {subject} not found.")
            return
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
        currentChat.message(channel, racer.display_name+"'s time has been updated.")
    elif command[0] == "!block":
        if len(command) != 2:
            return
        subject = command[1].lower()
        info = twitch.get_user_infos([subject])
        if info == None or len(info) == 0:
            currentChat.message(channel, f"Twitch username {subject} not found.", message_id)
            return
        info = info[0]
        subject_id = info['id']
        subject_displayname = info['display_name']
        if subject_id in users.blocklist:
            currentChat.message(channel, f"{subject_displayname} is already blocked.")
            return
        users.add(subject, subject_id, users.Role.BLOCKLIST)
        if subject_id in users.counters:
            users.remove(subject_id, users.Role.COUNTER)
        currentChat.message(channel, f"{subject_displayname} has been blocked.")
    elif command[0] == "!unblock":
        if len(command) != 2:
            return
        subject = command[1].lower()
        info = twitch.get_user_infos([subject])
        if info == None or len(info) == 0:
            currentChat.message(channel, f"Twitch username {subject} not found.", message_id)
            return
        info = info[0]
        subject_id = info['id']
        subject_displayname = info['display_name']
        if subject_id not in users.blocklist:
            currentChat.message(channel, f"{subject_displayname} is already not blocked.")
            return
        users.remove(subject_id, users.Role.BLOCKLIST)
        currentChat.message(channel, f"{subject_displayname} is no longer blocked.")
    elif command[0] == "!admin":
        if len(command) != 2:
            return
        subject = command[1].lower()
        info = twitch.get_user_infos([subject])
        if info == None or len(info) == 0:
            currentChat.message(channel, f"Twitch username {subject} not found.", message_id)
            return
        info = info[0]
        subject_id = info['id']
        subject_displayname = info['display_name']
        if subject_id in users.admins:
            currentChat.message(channel, f"{subject_displayname} is already an admin.")
            return
        users.add(subject, subject_id, users.Role.ADMIN)
        currentChat.message(channel, f"{subject_displayname} is now an admin.")
    elif command[0] == "!mmkill":
        obs.request("StopStream")
        currentChat.message(channel, "Permanently closing the bot now.")
        settings.doQuit = True
    elif command[0] == "!togglestream":
        obs.request("ToggleStream")
        currentChat.message(channel, "Toggled stream.")
    elif command[0] == "!fetchracers":
        settings.playersLock = True
        newRacers = gsheets.getRacers()
        sheet_racers_lower = []

        # add new racers from the sheet
        racers_added = []
        channels_to_join = []
        for r in newRacers:
            sheet_racers_lower.append(r.lower())
            if r.lower() not in playerLookup.keys():
                playerLookup[r.lower()] = player.Player(r, {})
                racers_added.append(playerLookup[r.lower()].display_name)
                channels_to_join.append(r.lower())
        if racers_added != []:
            currentChat.message(channel, f"Adding new racer(s) found on the Google spreadsheet: {', '.join(racers_added)}")
            twitch.get_player_infos_async(channels_to_join, playerLookup)
            currentChat.join(channels_to_join)
        
        # delete racers that have been removed from the sheet
        racers_removed = []
        channels_to_part = []
        for r in list(playerLookup.keys()):
            if r not in sheet_racers_lower:
                racers_removed.append(playerLookup[r].display_name)
                playerLookup.pop(r)
                channels_to_part.append(r)
        if racers_removed != []:
            currentChat.message(channel, f"Removing racers not found on the Google spreadsheet: {', '.join(racers_removed)}")
            currentChat.part(channels_to_part)

        if racers_added == [] and racers_removed == []:
            currentChat.message(channel, f"No changes were found between the bot's racer list and Google Sheets.")
            return
        
        # re-calculate the number of pages, redraw to remove old player cards
        settings.set_max_count(len(playerLookup))
        settings.redraw = True
        settings.playersLock = False
    elif command[0] == "!clearstats":
        for p in list(playerLookup.keys()):
            playerLookup[p].score = 0
            playerLookup[p].status = "live"
        currentChat.message(channel, f"Cleared all racer stats.")
        settings.redraw = True
    elif command[0] == "!clip":
        if len(command) > 1:
            subject = command[1].lower()
            info = twitch.get_user_infos([subject])
            if info == None or len(info) == 0:
                currentChat.message(channel, f"Twitch username {subject} not found.", message_id)
                return
            info = info[0]
            subject_id = info['id']
            twitch.create_clip_async(subject_id, subject)
