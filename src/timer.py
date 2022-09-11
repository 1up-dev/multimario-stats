import math
import datetime
import pygame
import settings

def drawTimer(screen):
    dur = (datetime.datetime.now() - settings.startTime).total_seconds()
    dur = math.floor(dur)
    
    negative = False
    if dur < 0:
        dur = dur * -1
        negative = True
    
    tmp1 = datetime.timedelta(seconds=math.floor(dur))
    delta = str(tmp1).split(" day")

    initialHours = 0
    extraHours=""
    if len(delta)==1:
        extraHours = delta[0]
    elif len(delta)==2:
        days = delta[0]
        days = int(days)
        initialHours = days * 24
        if delta[1][0]=="s":
            extraHours = delta[1][3:]
        elif delta[1][0]==",":
            extraHours = delta[1][2:]

    finalTime = extraHours.split(":")
    finalHours = int(finalTime[0]) + initialHours
    cur_time = str(finalHours)+":"+finalTime[1]+":"+finalTime[2]
    if negative:
        cur_time = "-"+cur_time
    #print(cur_time)

    border = pygame.Rect([0,0,400,100])
    border.center = (1277,84)
    pygame.draw.rect(screen, (200, 200, 200), border)
    r = pygame.Rect([0,0,394,94])
    r.center = (1277,84)
    pygame.draw.rect(screen, (40, 40, 40), r)
    timer = settings.getFont(65).render(cur_time, 1, (200,200,200))
    timer_r = timer.get_rect(center=(1277,84))#topright=, etc
    screen.blit(timer, timer_r)

    pygame.display.update(r)
    return cur_time
