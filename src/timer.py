import math
import datetime
import threading
import time
import pygame
import obs
import settings

stopped_time = None
timelimit_event = datetime.datetime.now()
clear_event = datetime.datetime.now()

def stop_stream_delayed():
    time.sleep(10)
    obs.request("StopStream")

def check_events(t, playerLookup):
    global timelimit_event, clear_event
    seconds_since_event = (datetime.datetime.now() - timelimit_event).total_seconds()
    if t == settings.modeInfo['time-limit'] and seconds_since_event > 5:
        for p in list(playerLookup.keys()):
            p = playerLookup[p]
            if p.status == "live":
                p.finish("disqualified")
        timelimit_event = datetime.datetime.now()
        settings.redraw = True

    seconds_since_event = (datetime.datetime.now() - clear_event).total_seconds()
    if t == "-0:30:00" and seconds_since_event > 5:
        for p in list(playerLookup.keys()):
            p = playerLookup[p]
            p.score = 0
            p.status = "live"
        clear_event = datetime.datetime.now()
        settings.redraw = True
        if settings.auto_stream_events:
            obs.request("StartStream")

def draw(screen, playerLookup, update_display=True):
    global stopped_time
    if settings.stopTimer == False:
        dur = (datetime.datetime.now() - settings.startTime).total_seconds()
        stopped_time = None
    else:
        if stopped_time == None:
            stopped_time = (datetime.datetime.now() - settings.startTime).total_seconds()
            if settings.auto_stream_events:
                t = threading.Thread(target=stop_stream_delayed, args=())
                t.daemon = True
                t.start()
        dur = stopped_time
    dur = math.floor(dur)
    time_str = settings.dur_to_str(dur)

    border = pygame.Rect([0,0,400,100])
    border.center = (1277,84)
    pygame.draw.rect(screen, (200, 200, 200), border)
    r = pygame.Rect([0,0,394,94])
    r.center = (1277,84)
    pygame.draw.rect(screen, (40, 40, 40), r)
    timer = settings.getFont(65).render(time_str, 1, (200,200,200))
    timer_r = timer.get_rect(center=(1277,84))#topright=, etc
    screen.blit(timer, timer_r)

    if update_display:
        pygame.display.update(border)
    check_events(time_str, playerLookup)
