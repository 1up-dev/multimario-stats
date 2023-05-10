# multimario-stats
This is the program that runs the scoreboard and Twitch chat bot for **[The 602 Race](https://docs.google.com/spreadsheets/d/1ludkWzuN0ZzMh9Bv1gq9oQxMypttiXkg6AEFvxy_gZk/)** and other Multi-Mario endurance races.  
See **[this video archive](https://www.twitch.tv/videos/857024553)** from December 2020 for an example of it in use.  
![Example](https://imgur.com/gap4Rol.png)

## What is the 602 Race?  
>The 602 Race is an endurance race to 100% completion of four 3D Super Mario games, with a total of 602 Stars to be collected.  
>The four games in order are: Super Mario 64: 120 Stars, Super Mario Galaxy: 120 Stars, Super Mario Sunshine: 120 Shines, and Super Mario Galaxy 2: 242 Stars.

## Technical info
- Rename `settings-template.json` to `settings.json` and fill out the fields before running.
- Running the program will make the bot active in the Twitch chats of all the racers and the extra chat rooms specified in `settings.json`.
- The Twitch username and authentication token (password) for the bot are pulled from `settings.json`. Get the authentication token here: http://twitchapps.com/tmi/.  
- The Twitch developer app Client-ID is for API requests. Get it here: https://dev.twitch.tv/dashboard/apps.  
- The Google API Key is used to get the list of racers from the race spreadsheet. Get it here: https://console.developers.google.com/apis/dashboard
- Setting `"debug": true` in `settings.json` will have a few effects:
    - The debug Google Sheets page (`"debug-gsheet"` in `settings.json`) will be used to get the list of racers instead of the official race sheet.
    - Each racer will be given pseudorandom stats for testing.
