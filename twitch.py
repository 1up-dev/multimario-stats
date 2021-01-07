import requests
import json
import urllib
import os

with open('settings.json', 'r') as f:
    j = json.load(f)
    AUTH = "Bearer " + j['twitch-api-auth']
    cId = j['twitch-api-clientid']

# Uses the Twitch API to fetch profile pictures of racers
def fetchProfiles(users):
    for user in users:
        if not os.path.isfile("./profiles/"+user+".png"):
            url = "https://api.twitch.tv/helix/users?login="+user
            headers = {"Client-ID":cId, "Authorization":AUTH}
            response = requests.get(url, headers=headers)
            if response.status_code in range(200,300):
                responseData = json.loads(response.content.decode("UTF-8"))['data']
                if len(responseData)==0:
                    print("[API] Twitch user "+user+" does not exist. Using default image.")
                    #playerLookup[user].validTwitchAccount = False
                else:
                    data = responseData[0]
                    profileLocation = data['profile_image_url']
                    urllib.request.urlretrieve(profileLocation, "."+"/profiles/"+user+".png")
                    print("[API] Fetched profile of Twitch user "+user+".")
            else:
                print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
                return None
    return

def getTwitchId(user):
    url = "https://api.twitch.tv/helix/users?login="+user
    headers = {"Client-ID":cId, "Authorization":AUTH}
    response = requests.get(url, headers=headers)
    if response.status_code in range(200,300):
        responseData = json.loads(response.content.decode("UTF-8"))['data']
        if len(responseData)==0:
            print("[API] Twitch user "+user+" does not exist.")
            return None
        else:
            id = responseData[0]['id']
            print("[API] Fetched id of Twitch user "+user+": "+id+".")
            return id
    else:
        print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
        return None

def updateSet(data):
    updated = {}
    for user in data:
        id = data[user]
        url = "https://api.twitch.tv/helix/users?id="+id
        headers = {"Client-ID":cId, "Authorization":AUTH}
        response = requests.get(url, headers=headers)
        if response.status_code in range(200,300):
            responseData = json.loads(response.content.decode("UTF-8"))['data']
            if len(responseData)==0:
                print("[API] Twitch id "+id+" does not exist.")
            else:
                newUsername = responseData[0]['login']
                updated[newUsername] = id
                if user != newUsername:
                    print("[API] Updated username of Twitch id "+id+": "+user+" -> "+newUsername)
        else:
            print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
            return None
    return updated
