import settings
import mode_602
import mode_1120
import mode_246
import mode_sandbox

def draw(screen, playerLookup, sortedRacers, page):
    if settings.mode == "602":
        return mode_602.draw(screen, playerLookup, sortedRacers, page)
    elif settings.mode == "1120":
        return mode_1120.draw(screen,playerLookup)
    elif settings.mode == "246":
        return mode_246.draw(screen, playerLookup, sortedRacers, 1)
    elif settings.mode == "sandbox":
        return mode_sandbox.draw(screen, playerLookup, sortedRacers, 1)

def hasCollected(score):
    if settings.mode == "602":
        return mode_602.collected(score)
    elif settings.mode == "1120":
        return mode_1120.collected(score)
    elif settings.mode == "246":
        return mode_246.collected(score)
    elif settings.mode == "sandbox":
        return mode_sandbox.collected(score)
