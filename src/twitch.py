import requests
import json
import urllib
import os
import threading
import time
import http.server
import socketserver
import webbrowser
import pygame
import settings

class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global twitch_auth_code
        if 'code=' in self.path:
            twitch_auth_code = self.path.split('code=')[1].split('&')[0]
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(b"multimario-stats: Received Twitch authorization.<br>You may close this page.")
        return

def req(method, url, headers={}, params={}):
    if method == "GET":
        response = requests.get(url, params=params, headers=headers)
    elif method == "POST":
        response = requests.post(url, params=params, headers=headers)
    else:
        return
    data = response.json()
    if response.status_code == 401:
        print(f"[API] 401 Invalid token. Attempting to refresh token. {data}")
        if validate_token():
            return req(method, url, headers, params)
        print("[API] Token refresh failed. Giving up on request.")
        return
    if response.status_code not in range(200,300):
        print(f"[API] Bad request. Giving up. ({response.status_code}): {data}")
        return
    return data

def get_player_infos(players):
    for player in players.values():
        get_player_info(player)

def get_player_info(player):
    response = get_user_info(player.name)
    if response == None:
        return
    path = settings.path(f"profiles/{player.name}.png")
    if not os.path.isfile(path):
        urllib.request.urlretrieve(response['profile_url'], path)
    player.profile = pygame.image.load(path)
    player.twitch_id = response['id']
    player.nameCaseSensitive = response['display_name']
    settings.redraw = True

def create_clip(broadcaster_id):
    time.sleep(20)
    headers = {"Client-Id":settings.twitch_clientid, "Authorization":f'Bearer {settings.twitch_token}'}
    params = {"broadcaster_id": broadcaster_id}
    response = req("POST", "https://api.twitch.tv/helix/clips", headers, params)
    if response == None:
        print(f"Clip request failed.")
        return
    responseData = response['data']
    if len(responseData) == 0 or 'edit_url' not in responseData[0]:
        print(f"Clip request failed. {response}")
        return
    print(responseData[0]['edit_url'])

def create_clip_async(broadcaster_id):
    t = threading.Thread(target=create_clip, args=(broadcaster_id,))
    t.daemon = True
    t.start()

def get_user_info(user):
    url = "https://api.twitch.tv/helix/users"
    headers = {"Client-ID":settings.twitch_clientid, "Authorization":f'Bearer {settings.twitch_token}'}
    params = {"login":user}
    response = req("GET", url, headers, params)
    if response == None:
        return
    responseData = response['data']
    if len(responseData)==0:
        print(f"[API] Twitch user {user} does not exist.")
        return
    data = responseData[0]
    user_info = {'profile_url': data['profile_image_url'], 
                 'id': data['id'],
                 'display_name': data['display_name']}
    return user_info

def updateSet(data):
    updated = {}
    for user in data:
        id = data[user]
        url = "https://api.twitch.tv/helix/users?id="+id
        headers = {"Client-ID":settings.twitch_clientid, "Authorization":f'Bearer {settings.twitch_token}'}
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

def validate_token():
    print("[API] Validating token...")

    # Validate token
    url = 'https://id.twitch.tv/oauth2/validate'
    headers = {'Authorization': f'OAuth {settings.twitch_token}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code in range(200,300):
        if data != None:
            settings.twitch_nick = data['login']
            print("[API] Token is valid.")
            return True
    print("[API] Token is invalid. Refreshing.", response.status_code, data)

    # Refresh token
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id": settings.twitch_clientid, "client_secret": settings.twitch_secret, "grant_type": "refresh_token", "refresh_token": settings.twitch_refresh_token}
    response = requests.post(url, params=params)
    data = response.json()
    if response.status_code in range(200,300):
        if data != None:
            settings.twitch_token = data['access_token']
            settings.twitch_refresh_token = data['refresh_token']
            settings.save_api_tokens_to_file()
            print("[API] Token refreshed.")
            return True
    print("[API] Token refresh failed. Requesting authorization from user.", response.status_code, data)

    # Request authorization from user
    global twitch_auth_code
    twitch_auth_code = ""
    port = 3000
    webbrowser.open(f"https://id.twitch.tv/oauth2/authorize?client_id={settings.twitch_clientid}&redirect_uri=http://localhost:{port}&response_type=code&scope=clips:edit+chat:edit+chat:read+whispers:edit+whispers:read")
    with socketserver.TCPServer(("localhost", port), HTTPHandler) as server:
        print(f"[API] HTTP server waiting for Twitch authorization at localhost:{port}")
        server.handle_request()
    if twitch_auth_code == "":
        print("[API] Authorization request failed.")
        return False

    # Request new token
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id":settings.twitch_clientid, "client_secret":settings.twitch_secret, "code":twitch_auth_code, "grant_type":"authorization_code", "redirect_uri":f"http://localhost:{port}"}
    response = requests.post(url, params=params)
    data = response.json()
    if response.status_code not in range(200,300):
        print("[API] New token request failed.", response.status_code, data)
        return False
    if data == None:
        print("[API] New token request failed.", response.status_code, data)
        return False
    settings.twitch_token = data["access_token"]
    settings.twitch_refresh_token = data["refresh_token"]
    settings.save_api_tokens_to_file()
    print("[API] New token received. Validating...")
    
    # Validate token
    url = 'https://id.twitch.tv/oauth2/validate'
    headers = {'Authorization': f'OAuth {settings.twitch_token}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code in range(200,300):
        if data != None:
            settings.twitch_nick = data['login']
            print("[API] Token is valid.")
            return True
    print("[API] New token is invalid. Giving up.")
    return False
