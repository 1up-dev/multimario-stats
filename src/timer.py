import math
import datetime
import pygame
import settings

stopped_time = ""

def drawTimer(screen):
    global stopped_time
    if settings.stopTimer and stopped_time == "":
        stopped_time = (datetime.datetime.now() - settings.startTime).total_seconds()
    if settings.stopTimer == False:
        dur = (datetime.datetime.now() - settings.startTime).total_seconds()
        stopped_time = ""
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
    return time_str
