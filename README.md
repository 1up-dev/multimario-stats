# 602Stats
This is the program that runs the scoreboard and Twitch chat bot for [The 602 Race](https://docs.google.com/spreadsheets/d/1ludkWzuN0ZzMh9Bv1gq9oQxMypttiXkg6AEFvxy_gZk/).


## The 602 Race Stats Stream commands:

### **Commands for Updaters:**
#### !add [twitchname] [number]
- This adds to the total number of stars for [twitchname]. 
- It will update game completion as appropriate. 
- Positive and negative numbers are accepted.


### **Commands for Racers:**
#### !add [number]
- Positive and negative numbers are accepted.
#### !quit
- Quit the race. An admin can undo this if necessary.
#### !mod [twitchname]
- Adds [twitchname] as a star count updater.
#### !unmod [twitchname]
- Removes [twitchname] as a star count updater.


### **Commands for Admins:**
#### !start
- Sets the start time of the race to the current time. 
#### !start [date & time]
- Sets the start time of the race to the specified time.
- Must be in this format: 2018-12-29@09:00

#### !mod [twitchname]
#### !unmod [twitchname]

#### !forcequit [twitchname]
#### !noshow [twitchname]
#### !dq [twitchname]

#### !revive [twitchname]
- Undo a quit, dq, or noshow.
