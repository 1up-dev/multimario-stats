import os
import math
import copy
import pygame
import settings
import mode_540
import timer
from settings import getFont

games = copy.deepcopy(settings.modeInfo['games'])
for g in games:
    g['background']= pygame.image.load(os.path.join(settings.baseDir,g['background']))
    g['icon']= pygame.image.load(os.path.join(settings.baseDir,g['icon']))
finishBG = pygame.image.load(os.path.join(settings.baseDir,settings.modeInfo['finish-bg']))
background = pygame.image.load(os.path.join(settings.baseDir,'resources/background.png'))

slots = [
    (7,12), (325,12), (643,12), #(961,12), (1279,12),
    (7,169),(325,169),(643,169),(961,169),(1279,169),
    (7,315),(325,315),(643,315),(961,315),(1279,315),
    (7,461),(325,461),(643,461),(961,461),(1279,461),
    (7,607),(325,607),(643,607),(961,607),(1279,607),
    (7,753),(325,753),(643,753),(961,753),(1279,753),
    (1600,900)
]
length = 314
height = 142

def draw(screen, playerLookup, sortedRacers, page):
    if settings.playersLock:
        # indicates !fetchracers is currently running. 
        # playerLookup size could change during draw, causing error
        return screen
    if settings.mode == "540":
        return mode_540.draw(screen, playerLookup, sortedRacers, page)
    
    screen.blit(pygame.transform.scale(background, (1600,900)), (0,0))
    timer.drawTimer(screen, playerLookup)
    
    x,y = -1,-1
    if page != 0:
        x = 3
        y = 2 + page * 25
    slot = 0
    for i, r in enumerate(sortedRacers):
        if x <= i <= y or slot >= len(slots):
            playerLookup[r].corner = None
            continue
        playerLookup[r].corner = slots[slot]
        slot += 1

    #-----------scorecard drawing------------
    for key in playerLookup:
        player = playerLookup[key]
        corner = player.corner
        if corner == None:
            continue
        
        pygame.draw.rect(screen, (200, 200, 200), [corner[0], corner[1], 314, 142])
        pygame.draw.rect(screen, (25, 25, 25), [corner[0]+2, corner[1]+2, 310, 138])

        score = player.score
        if player.status == "live":
            bg = None
            gameCounts, barLengths, gameMaxes = [], [], []
            done = False
            smallBar, largeBar, barHeight = 110, 260, 20
            for i, g in enumerate(games):
                gameCounts.append(0)
                if done:
                    pass
                elif score <= g['count']:
                    bg = g['background']
                    if score == g['count']:
                        if i+1 <= len(games)-1:
                            bg = games[i+1]['background']
                        else:
                            print(f"Error: {player.nameCaseSensitive} has {player.score} (max score) while live.")
                            player.status = "done"
                            bg = games[i]['background']
                    gameCounts[-1] = score
                    done = True
                    score -= g['count']
                else:
                    gameCounts[-1] = g['count']
                    score -= g['count']
                gameMaxes.append(g['count'])
                barLengths.append(math.floor((gameCounts[-1]/g['count'])*smallBar))

            img = pygame.transform.scale(bg,(310,138))
            screen.blit(img, (corner[0]+2, corner[1]+2))

            # base boxes
            s = pygame.Surface((smallBar+4, barHeight), pygame.SRCALPHA)
            s.fill((60,60,60,192))
            screen.blit(s, (40+corner[0], 80+corner[1]) )
            screen.blit(s, (190+corner[0], 80+corner[1]) )
            screen.blit(s, (40+corner[0], 110+corner[1]) )
            if len(games) == 4:
                screen.blit(s, (190+corner[0], 110+corner[1]) )
            
            boxYs=[80+corner[1]+2, 110+corner[1]+2, 80+corner[1]+2, 110+corner[1]+2]

            # filled boxes
            gray = (150,150,150)
            rects = []
            rects.append(pygame.draw.rect(screen, gray, [40+corner[0]+2, 80+corner[1]+2, barLengths[0], barHeight-4]))
            rects.append(pygame.draw.rect(screen, gray, [40+corner[0]+2, 110+corner[1]+2, barLengths[1], barHeight-4]))
            rects.append(pygame.draw.rect(screen, gray, [190+corner[0]+2, 80+corner[1]+2, barLengths[2], barHeight-4]))
            if len(games) == 4:
                rects.append(pygame.draw.rect(screen, gray, [190+corner[0]+2, 110+corner[1]+2, barLengths[3], barHeight-4]))

            # individual game counts
            for i in range(len(gameCounts)):
                if gameCounts[i] < gameMaxes[i]/2:
                    label = getFont(18).render(str(gameCounts[i]), 1, (220,220,220))
                    y = rects[i].midright[1]
                    # if the box is empty, manually center the y coordinate on the middle of the bar instead of the default top
                    if y == boxYs[i]:
                        y += 8
                    label_r = label.get_rect(midleft=(rects[i].midright[0]+2, y))
                else:
                    label = getFont(18).render(str(gameCounts[i]), 1, (60,60,60))
                    label_r = label.get_rect(midright=(rects[i].midright[0]-2, rects[i].midright[1]))
                screen.blit(label, label_r)

            # game icons
            for i, g in enumerate(games):
                if i == 0:
                    x, y = 6, 75
                elif i == 1:
                    x, y = 6, 103
                elif i == 2:
                    x, y = 157, 70
                elif i == 3:
                    x, y = 157, 108
                screen.blit(g['icon'], (x+corner[0], y+corner[1]))

        elif player.status == "done":

            bg = pygame.transform.scale(finishBG,(310,138))
            screen.blit(bg, (corner[0]+2, corner[1]+2))

            # screen.blit(finishBG, (playerLookup[key].corner[0], playerLookup[key].corner[1]))
            doneTag = getFont(60).render("Done!", 1, (220,220,220))
            done_r = doneTag.get_rect(center=((player.corner[0]+(length/2), 85+player.corner[1])))
            screen.blit(doneTag, done_r)

            label = getFont(24).render(str("Final Time: {0}".format(player.duration_str)), 1, (220,220,220))
            label_r = label.get_rect(center=((player.corner[0]+(length/2), 125+player.corner[1])))
            screen.blit(label, label_r)
        
        else:
            text = ""
            offset = 0
            label = getFont(23).render("Completion: "+str(score)+"/"+str(settings.max_score) +" in "+player.duration_str, 1, (220,220,220))
            if player.status == "quit":
                text = "Quit"
            elif player.status == "disqualified":
                text = "Disqualified"
            elif player.status == "noshow":
                label = getFont(20).render("", 1, (220,220,220))
                text = "No-Show"
                offset = 10
            
            textTag = getFont(48).render(text, 1, (255, 0, 0))
            text_r = textTag.get_rect(center=(player.corner[0]+(length/2), player.corner[1]+80+offset))
            screen.blit(textTag, text_r)
            label_r = label.get_rect(center=(player.corner[0]+(length/2), player.corner[1]+123))
            screen.blit(label, label_r)

        
        #-------scorecard header-------
        #profile picture
        prof = pygame.transform.scale(player.profile, (50,50))
        screen.blit(prof, (8+player.corner[0], 8+player.corner[1])) 

        #name & place
        color = (220,220,220)
        if player.place <=3:
            color = (239,195,0)
        nameRender = getFont(24).render(str(player.nameCaseSensitive), 1, color)
        placeRender = getFont(40).render(str(player.place), 1, color)

        screen.blit(nameRender, (65+player.corner[0], 15+player.corner[1]))
        #topright justify the place text
        place_r = placeRender.get_rect(topright=(player.corner[0]+304,player.corner[1]+5))
        screen.blit(placeRender, place_r)


    pygame.display.flip()
    return screen
