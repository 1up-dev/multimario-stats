import mode_602
import mode_1120
import mode_246

def draw(screen, mode, playerLookup, sortedRacers, page):
    if mode == "602":
        return mode_602.draw(screen, playerLookup, sortedRacers, page)
    elif mode == "1120":
        return mode_1120.draw(screen,playerLookup)
    if mode == "246":
        return mode_246.draw(screen, playerLookup, sortedRacers, 1)