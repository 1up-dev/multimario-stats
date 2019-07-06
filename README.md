# 602Stats
This is the program that runs the scoreboard and Twitch chat bot for [The 602 Race](https://docs.google.com/spreadsheets/d/1ludkWzuN0ZzMh9Bv1gq9oQxMypttiXkg6AEFvxy_gZk/).  
See [this video archive](https://www.twitch.tv/videos/356727983) from December 2018 for an example of it in use.  
![Example](https://i.imgur.com/vZSinTe.jpg)

## What is the 602 Race?  
>The 602 Race is a race to 100% completion of four 3D Super Mario games, for a total of 602 stars.  
>The four games in order are:  Super Mario 64: 120 Stars, Super Mario Galaxy: 120 Stars, Super Mario Sunshine: 120 Shines, and Super Mario Galaxy 2: 242 Stars.
  
## Stats stream bot commands:
### **Commands for Anyone:**
#### !status
- Shows the roles of the user that issued the command.
#### !status [twitchname]
- Shows the roles of [twitchname]

### **Commands for Updaters:**
**Note: Moderators of the Twitch channel the bot is in are automatically allowed to update. They do not have to be whitelisted manually.**
#### !add [twitchname] [number]
- This adds to the total number of stars for [twitchname]. 
- It will update game completion as appropriate. 
- Positive and negative numbers are accepted.
   
### **Commands for Racers:**
#### !add [number]
- Positive and negative numbers are accepted.
#### !quit
- Quit the race. An admin can undo this if necessary.
#### !unfinish
- Re-enter the race after accidentally finishing too early.
#### !mod/!unmod [twitchname]
- Adds or removes [twitchname] as a star count updater.
  
### **Commands for Admins:**
#### !start
- Sets the start time of the race to the current time. 
#### !start [date & time]
- Sets the start time of the race to the specified time.
- Must be in this format: 2018-12-29@09:00
#### !mod/!unmod [twitchname]
#### !forcequit/!noshow/!dq [twitchname]
#### !revive [twitchname]
- Undo a quit, dq, noshow, or finish.
#### !settime [twitchname] [duration]
- Set a racer's run duration on the "done" or "quit" card.
- Must be in this format: 32:59:59
#### !blacklist/!unblacklist [twitchname]
- Add/remove a user to the updater blacklist, preventing them from updating star counts.
#### !admin [twitchname]
  
## Before you attempt to run the program
- WARNING: Running the program will join all the Twitch chats specified in racers.txt and make the bot active. Make sure racers.txt has the correct names in it before starting.  
- The program pulls the Twitch username and password (authentication token) for the bot from settings.txt. Get the authentication token from http://twitchapps.com/tmi/.  
- The Twitch developer app Client-ID is for API requests, get it from https://dev.twitch.tv/dashboard/apps.  
- The Google API Key is to get the list of racers from the 602 Race spreadsheet. Get it here: https://console.developers.google.com/apis/dashboard
- admins.txt, racers.txt, updaters.txt, and blacklist.txt contain only Twitch usernames separated by newlines.  
