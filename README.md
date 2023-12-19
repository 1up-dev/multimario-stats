# multimario-stats
This is the program that runs the scoreboard and Twitch chat bot for **[The 602 Race](https://docs.google.com/spreadsheets/d/1ludkWzuN0ZzMh9Bv1gq9oQxMypttiXkg6AEFvxy_gZk/)** and other Multi-Mario endurance races.  
See **[this video archive](https://www.twitch.tv/videos/1856764496)** for an example of it in use.  
![Example](https://i.imgur.com/bHeYEUO.jpg)

## What is the 602 Race?  
>The 602 Race is an endurance race to 100% completion of four 3D Mario games, with a total of 602 Stars to be collected.  
>The four games in order are: Super Mario 64: 120 Stars, Super Mario Galaxy: 120 Stars, Super Mario Sunshine: 120 Shines, and Super Mario Galaxy 2: 242 Stars.

## Features
- Displays a scoreboard for a multi-game race, with individual game completion bars and a timer.
- Dynamic number of racers: adding more racers will overflow the scoreboard to a new "page", which will be automatically cycled through to make all racers' scorecards visible.
- Twitch chat users update racer scores using commands with an included custom Twitch chat bot.
- The bot joins all racers' Twitch chat rooms automatically for convenience, and can join any other Twitch chat if requested.
- Any Twitch chat user can check the current status of any racer and check who is currently in a specific place.
- Support for multiple categories: races with different games and score counts can be easily created using JSON.
- Automatically starts/stops the livestream using OBS WebSocket server when the race is about to begin and after it finishes.
- Nearly all functionality is accessible for Admin users using Twitch chat commands:
    - Set the start time of the race to a specific date and time to make the onscreen timer and final racer durations accurate.
    - Disqualify racers, give them a tag of "No-show", or force-quit them if they forgot to: this info is displayed on the scoreboard.
    - Allow and block specific Twitch users from updating scores to reduce disruption.
    - Set the final racer duration manually for any racer whose scorecard is inaccurate.
    - Update the list of racers: the program will check a Google Sheets page for changes.
    - Manually start/stop the livestream at any point.

## Running the program
- Install the Python modules from `requirements.txt`, optionally inside a virtual environment.
- Rename `settings-template.json` to `settings.json` and fill out the three API key fields by following the below instructions.
- `twitch-api-clientid`, `twitch-api-secret`: The bot gets its login info and makes API requests using a Twitch developer application. Register an application here: https://dev.twitch.tv/console. Add `http://localhost:3000` as an OAuth Redirect URL, then copy the `Client ID` and `Client Secret` into `settings.json`. After you start the program, it will open a browser window and prompt you to grant access using your desired account for the bot. If you need to open this access request in another browser to use the correct Twitch account, just copy and paste the URL. It will still work.
- `google-api-key`: The Google API Key is used to get the list of racers from Google Sheets. Create a new project with access to the Google Sheets API here: https://console.developers.google.com/apis/dashboard.
- Run the program by running `src/multimario-stats.py` with the desired Python executable. ⚠️ Running the program will make the bot active in the Twitch chats of all the racers.
- For the OBS start- and stop-stream functionality to work, open your desired streaming profile on OBS, go to the Tools menu at the top of the window, and select `WebSocket Server Settings`. Check `Enable WebSocket server`, set `Server Port` to `4455`, and **un**check `Enable Authentication`.
- Setting `"testing-gsheet"` in `settings.json` will enable testing mode:
    - The provided testing Google Sheet will be used to get the list of racers instead of the official race sheet.
    - Racer status updates (done, quit, etc) will not be mirror-posted in the main channel, to avoid spam while testing.
