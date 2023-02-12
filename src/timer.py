import math
import datetime
import pygame
from pynput.keyboard import Key, Controller
import settings

stopped_time = None
time_limit_reached = False
stats_cleared = False

def check_events(t, playerLookup):
    global time_limit_reached, stats_cleared
    if t == settings.modeInfo['time-limit'] and time_limit_reached == False:
        for p in playerLookup:
            p = playerLookup[p]
            if p.status == "live":
                p.finish("disqualified")
        time_limit_reached = True
        settings.redraw = True
        # toggle stream (off)
        kb = Controller()
        with kb.pressed(Key.ctrl):
            kb.tap("5")

    if t == "-0:15:00" and stats_cleared == False:
        for p in playerLookup:
            p = playerLookup[p]
            p.score = 0
            p.status = "live"
        stats_cleared = True
        settings.redraw = True
        # toggle stream (on)
        kb = Controller()
        with kb.pressed(Key.ctrl):
            kb.tap("5")

def drawTimer(screen, playerLookup):
    global stopped_time
    if settings.stopTimer and stopped_time == None:
        stopped_time = (datetime.datetime.now() - settings.startTime).total_seconds()
    if settings.stopTimer == False:
        dur = (datetime.datetime.now() - settings.startTime).total_seconds()
        stopped_time = None
    else:
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

    pygame.display.update(r)
    check_events(time_str, playerLookup)
