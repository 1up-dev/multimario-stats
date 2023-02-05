import socket
import datetime
import time
import traceback
import settings

class ChatRoom:
    def __init__(self, channels):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.NICK = settings.twitch_nick
        self.PASS = settings.twitch_pw
        self.channels = channels
        self.currentSocket = socket.socket()
        self.msgCount = 0
        self.msgPeriod = datetime.datetime.now()
        self.readbuffer = ""
        socket.setdefaulttimeout(480) # 8 minutes
        self.reconnect()
    def send(self, msg):
        try:
            self.currentSocket.send(bytes(f"{msg}\r\n", "UTF-8"))
        except ConnectionResetError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket: ConnectionResetError")
        except OSError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket error: {traceback.format_exc()}")
    def recv(self):
        try:
            self.readbuffer = self.readbuffer + self.currentSocket.recv(4096).decode("UTF-8", errors = "ignore")
            if self.readbuffer == "":
                print(datetime.datetime.now().isoformat().split(".")[0], "Socket: empty readbuffer")
        except ConnectionResetError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket: ConnectionResetError")
            self.readbuffer = ""
        except TimeoutError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket: TimeoutError. Attempting to reconnect...")
            self.readbuffer = ""
        except OSError:
            print(f"{datetime.datetime.now().isoformat().split('.')[0]} Socket error: {traceback.format_exc()}")
            self.readbuffer = ""
        if self.readbuffer == "":
            self.reconnect()
            return ""
        tmp = self.readbuffer.split('\n')
        self.readbuffer = tmp.pop()
        return tmp
    def message(self, channel, msg):
        timer = (datetime.datetime.now() - self.msgPeriod).total_seconds()
        if timer > 30:
            self.msgPeriod = datetime.datetime.now()
            self.msgCount = 0
        elif self.msgCount >= 20:
            time.sleep(30-timer)
            self.msgPeriod = datetime.datetime.now()
            self.msgCount = 0
        self.msgCount += 1
        self.send(f"PRIVMSG {channel} :{msg}")
        time.sleep(0.5)
    def part(self, channel):
        self.message(f"#{channel}", f"Now leaving #{channel}.")
        self.send(f"PART #{channel}")
        time.sleep(0.5)
        self.channels.remove(channel)
    def join(self, channel):
        self.send(f"JOIN #{channel}")
        time.sleep(0.5)
        self.message(f"#{channel}", f"Now joined #{channel}.")
        self.channels.append(channel)
    def reconnect(self):
        self.currentSocket.close()
        self.currentSocket = socket.socket()
        self.readbuffer = ""
        while True:
            try:
                self.currentSocket.connect((self.HOST,self.PORT))
            except Exception:
                time.sleep(10)
                continue
            break
        self.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
        self.send(f"PASS {self.PASS}")
        self.send(f"NICK {self.NICK}")
        # Join Twitch channels in batches of 20 or less, to comply with rate limiting.
        print("Joining Twitch channels...")
        j = 0
        while True:
            channel_list = "#"+",#".join(self.channels[j:j+20])
            self.send(f"JOIN {channel_list}")
            j += 20
            if self.channels[j:j+20] == []:
                break
            print("Sleeping 10 seconds before joining next batch of channels...")
            time.sleep(10.1)
        print("Done joining Twitch channels.")
        time.sleep(1)
    def pong(self, msg):
        self.send(msg)
