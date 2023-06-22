import socket
import datetime
import time
import traceback
import threading
import settings

class ChatRoom:
    def __init__(self, channels):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.channels = channels
        self.currentSocket = socket.socket()
        self.msgCount = 0
        self.msgPeriod = datetime.datetime.now()
        self.readbuffer = ""
        socket.setdefaulttimeout(480) # 8 minutes
        self.last_connect_time = None
        self.reconnect()
    def send(self, msg):
        try:
            self.currentSocket.send(bytes(f"{msg}\r\n", "UTF-8"))
        except ConnectionResetError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket send: ConnectionResetError")
        except OSError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket send: {traceback.format_exc()}")
    def recv(self):
        try:
            self.readbuffer = self.readbuffer + self.currentSocket.recv(4096).decode("UTF-8", errors = "ignore")
            if self.readbuffer == "":
                print(datetime.datetime.now().isoformat().split(".")[0], "Socket recv: empty readbuffer")
        except ConnectionAbortedError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket recv: ConnectionAbortedError")
            self.readbuffer = ""
        except ConnectionResetError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket recv: ConnectionResetError")
            self.readbuffer = ""
        except TimeoutError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket recv: TimeoutError")
            self.readbuffer = ""
        except OSError:
            if settings.doQuit:
                return []
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket recv: {traceback.format_exc()}")
            self.readbuffer = ""
        if self.readbuffer == "":
            self.reconnect()
            return []
        tmp = self.readbuffer.split('\n')
        self.readbuffer = tmp.pop()
        return tmp
    def message(self, channel, msg, reply_id=None):
        if len(msg) > 300:
            msg = msg[:300] + "... (Message cut due to length)"
        timer = (datetime.datetime.now() - self.msgPeriod).total_seconds()
        if timer > 30:
            self.msgPeriod = datetime.datetime.now()
            self.msgCount = 0
        elif self.msgCount >= 20:
            time.sleep(30-timer)
            self.msgPeriod = datetime.datetime.now()
            self.msgCount = 0
        self.msgCount += 1
        if reply_id == None:
            self.send(f"PRIVMSG {channel} :{msg}")
        else:
            self.send(f"@reply-parent-msg-id={reply_id} PRIVMSG {channel} :{msg}")
        # Log the outgoing message to the log file for readability
        path = f"irc/{channel[1:]}.log"
        with open(settings.path(path), 'a+') as f:
            f.write(f"{datetime.datetime.now().isoformat().split('.')[0]} (Bot outgoing) {settings.twitch_nick}: {msg} \n")
        time.sleep(0.5)
    def part(self, channels):
        for channel in channels:
            self.channels.remove(channel)
        t = threading.Thread(target=self.join_part_channels, args=("PART", channels,))
        t.daemon = True
        t.start()
    def join(self, channels):
        self.channels += channels
        t = threading.Thread(target=self.join_part_channels, args=("JOIN", channels,))
        t.daemon = True
        t.start()
    def reconnect(self):
        if self.last_connect_time != None:
            dur = (datetime.datetime.now() - self.last_connect_time).total_seconds()
            if dur < 30:
                print("Last connection attempt was less than 30 seconds ago. Waiting before connecting again to avoid rate limit.")
                time.sleep(30 - dur)
        self.last_connect_time = datetime.datetime.now()
        if settings.twitch_nick != "" and settings.twitch_nick not in self.channels:
            self.channels = [settings.twitch_nick] + self.channels
        self.currentSocket.close()
        self.currentSocket = socket.socket()
        self.currentSocket.settimeout(480) # 8 minutes
        self.readbuffer = ""
        while True:
            try:
                self.currentSocket.connect((self.HOST,self.PORT))
            except Exception:
                time.sleep(10)
                continue
            break
        self.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
        self.send(f"PASS oauth:{settings.twitch_token}")
        self.send(f"NICK {settings.twitch_nick}")
        t = threading.Thread(target=self.join_part_channels, args=("JOIN", self.channels,))
        t.daemon = True
        t.start()
        time.sleep(1)
    def pong(self, msg):
        self.send(msg)
    def join_part_channels(self, direction, channels):
        if direction not in ["JOIN", "PART"]:
            print("[IRC] Invalid join/part arguments")
            return
        # Join Twitch channels in batches of 20 or less, to comply with rate limiting.
        print(f"{direction}ing Twitch channels: {channels}")
        j = 0
        while True:
            self.last_connect_time = datetime.datetime.now()
            channel_list = "#"+",#".join(channels[j:j+20])
            self.send(f"{direction} {channel_list}")
            j += 20
            if channels[j:j+20] == []:
                break
            time.sleep(11)
