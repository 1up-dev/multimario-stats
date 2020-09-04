import pygame
import math

star  = pygame.image.load('./resources/star.png')
shine = pygame.image.load('./resources/shine.png')
luma  = pygame.image.load('./resources/luma.png')
yoshi = pygame.image.load('./resources/yoshi.png')
background = pygame.image.load('./resources/background.png')
sm64BG = pygame.image.load('./resources/sm64.png')
smgBG = pygame.image.load('./resources/smg.png')
smsBG = pygame.image.load('./resources/sms.png')
smg2BG = pygame.image.load('./resources/smg2.png')
finishBG = pygame.image.load('./resources/finish_602.png')

#387 x 175 scorecards
# slots = [
#     (10,160),(407,160),(804,160),(1201,160),
#     (10,345),(407,345),(804,345),(1201,345),
#     (10,530),(407,530),(804,530),(1201,530),
#     (10,715),(407,715),(804,715),(1201,715), (1600,900)
# ]
#314 x 174 scorecards
slots = [
    (5,5),  (324,5),  (643,5),  (962,5),  (1281,5),
    (5,184),(324,184),(643,184),(962,184),(1281,184),
    (5,363),(324,363),(643,363),(962,363),(1281,363),
    (5,542),(324,542),(643,542),(962,542),(1281,542),
    (5,721),(324,721),(643,721),(962,721),(1281,721),
    (1600,900)
]

def collected(tempStars):
    game=""
    buffer=""
    noun="Star"
    if tempStars <= 120:
        game="Super Mario 64"
    elif tempStars <= 240:
        game="Super Mario Galaxy"
        tempStars -= 120
    elif tempStars <= 360:
        game="Super Mario Sunshine"
        tempStars -= 240
        noun="Shine"
    elif tempStars <= 602:
        game="Super Mario Galaxy 2"
        tempStars -= 360
    if tempStars != 1:
        buffer = "s"
    return " now has " + str(tempStars) + " "+ noun+buffer + " in " + game + "."

def getFont(size):
    return pygame.font.Font("./resources/Lobster 1.4.otf", size)

def draw(screen, playerLookup):
    screen.blit(pygame.transform.scale(background, (1600,900)), (0,0))

    for key in playerLookup:
        playerLookup[key].backup()

    #------sorting runners for display------
    sortedRacers = []
    for key in playerLookup:
        if len(sortedRacers) == 0:
            sortedRacers.append(key)
        elif playerLookup[key].collects == 602:
            for index, racer in enumerate(sortedRacers):
                if playerLookup[racer].collects < 602:
                    sortedRacers.insert(index, key)
                    break
                elif playerLookup[key].duration < playerLookup[racer].duration:
                    sortedRacers.insert(index, key)
                    break
                elif index == len(sortedRacers)-1:
                    sortedRacers.append(key)
                    break
        else:
            for index, racer in enumerate(sortedRacers):
                if playerLookup[key].collects >= playerLookup[racer].collects:
                    sortedRacers.insert(index, key)
                    break
                elif index == len(sortedRacers)-1:
                    sortedRacers.append(key)
                    break

    #---------place number assignments--------
    for index, racer in enumerate(sortedRacers):
        if index == 0:
            playerLookup[racer].place = 1
        else:
            current = playerLookup[racer]
            previous = playerLookup[sortedRacers[index-1]]
            if current.collects != 602:
                if current.collects == previous.collects:
                    current.place = previous.place
                else:
                    playerLookup[racer].place = index+1
            else:
                playerLookup[racer].place = index+1

    #------------slot assignments-----------
    for index, p in enumerate(sortedRacers):
        if index+2 < 25:
            playerLookup[p].corner = slots[index+2]
        else:
            playerLookup[p].corner = slots[25]

    # racerIndex=0
    # for s in range(0,25):
    #     if s <= 2: #leaving empty slots for spacing
    #         pass
    #     elif racerIndex < 25:
    #         playerLookup[sortedRacers[racerIndex]].corner = slots[s]
    #         racerIndex+=1
    #     else:
    #         playerLookup[sortedRacers[racerIndex]].corner = [1600, 900]
    #         racerIndex+=1

    #-----------scorecard drawing------------
    for key in playerLookup:
        currentPlayer = playerLookup[key]
        corner = currentPlayer.corner
        #pygame.draw.rect(screen, (25, 25, 25), [corner[0]-3, corner[1]-3, 393, 181])
        pygame.draw.rect(screen, (25, 25, 25), [corner[0], corner[1], 314, 174])

        score = currentPlayer.collects
        if currentPlayer.status == "live":
            # if currentPlayer.place <=3:
            #     completion = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (239,195,0))
            # else:
            #     completion = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (140,140,156))
            # screen.blit(completion, (62+currentPlayer.corner[0], 32+currentPlayer.corner[1]))

            sm64count = 0
            smgcount = 0
            smscount = 0
            smg2count = 0
            if score < 120:
                test = pygame.transform.scale(sm64BG,(306,166))
                screen.blit(test, (corner[0]+4, corner[1]+4))
                sm64count = score
            elif score < 240:
                test = pygame.transform.scale(smgBG,(306,166))
                screen.blit(test, (corner[0]+4, corner[1]+4))
                sm64count = 120
                smgcount = score-120
            elif score < 360:
                test = pygame.transform.scale(smsBG,(306,166))
                screen.blit(test, (corner[0]+4, corner[1]+4))
                sm64count = 120
                smgcount = 120
                smscount = score-240
            elif score < 602:
                test = pygame.transform.scale(smg2BG,(306,166))
                screen.blit(test, (corner[0]+4, corner[1]+4))
                sm64count = 120
                smgcount = 120
                smscount = 120
                smg2count = score-360

            smallBar = 110 #136
            largeBar = 260 #322
            barHeight = 20
            sm64length = math.floor((sm64count/120)*smallBar)
            smglength = math.floor((smgcount/120)*largeBar)
            smslength = math.floor((smscount/120)*smallBar)
            smg2length = math.floor((smg2count/242)*largeBar)

            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 80+corner[1], smallBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 110+corner[1], largeBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [190+corner[0], 80+corner[1], smallBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 140+corner[1], largeBar+4, barHeight])
            if score > 0:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 80+corner[1]+2, sm64length, barHeight-4])
            if score > 120:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 110+corner[1]+2, smglength, barHeight-4])
            if score > 240:
                pygame.draw.rect(screen, (150,150,150,254), [190+corner[0]+2, 80+corner[1]+2, smslength, barHeight-4])
            if score > 360:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 140+corner[1]+2, smg2length, barHeight-4])

            sm64color = (220,220,220)
            smscolor = (220,220,220)
            smgcolor = (220,220,220)
            smg2color = (220,220,220)
            if sm64count > 9:
                sm64color = (60,60,60)
            if smgcount > 9:
                smgcolor = (60,60,60)
            if smscount > 9:
                smscolor = (60,60,60)
            if smg2count > 9:
                smg2color = (60,60,60)

            #------------individual game scores & icons--------------
            screen.blit(star, (6+corner[0], 75+corner[1]) )
            label = getFont(18).render(str(sm64count), 1, sm64color)
            screen.blit(label, (45+corner[0], 79+corner[1]))

            screen.blit(luma, (6+corner[0], 103+corner[1]) )
            label = getFont(18).render(str(smgcount), 1, smgcolor)
            screen.blit(label, (45+corner[0], 109+corner[1]))

            screen.blit(shine, (157+corner[0], 70+corner[1]) )
            label = getFont(18).render(str(smscount), 1, smscolor)
            screen.blit(label, (195+corner[0], 79+corner[1]))

            screen.blit(yoshi, (6+corner[0], 137+corner[1]) )
            label = getFont(18).render(str(smg2count), 1, smg2color)
            screen.blit(label, (45+corner[0], 139+corner[1]))

        elif currentPlayer.status == "done":    #shows done tag

            test = pygame.transform.scale(finishBG,(306,166))
            screen.blit(test, (corner[0]+4, corner[1]+4))

            # screen.blit(finishBG, (playerLookup[key].corner[0], playerLookup[key].corner[1]))
            doneTag = getFont(70).render("Done!", 1, (220,220,220))
            screen.blit(doneTag, (90+currentPlayer.corner[0], 65+currentPlayer.corner[1]))

            label = getFont(24).render(str("Final Time: {0}".format(currentPlayer.completionTime)), 1, (220,220,220))
            screen.blit(label, (70+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "quit":    #shows quit tag

            quitTag = getFont(70).render("Quit", 1, (255, 0, 0))
            screen.blit(quitTag, (100+currentPlayer.corner[0], 55+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602 in "+currentPlayer.completionTime, 1, (220,220,220))
            screen.blit(label, (5+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "disqualified":    #shows disqualified tag
            forfeitTag = getFont(50).render("Disqualified", 1, (255, 0, 0))
            screen.blit(forfeitTag, (40+currentPlayer.corner[0], 70+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602", 1, (220,220,220))
            screen.blit(label, (65+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "noshow":    #shows no-show tag
            forfeitTag = getFont(50).render("No-Show", 1, (255, 0, 0))
            screen.blit(forfeitTag, (75+currentPlayer.corner[0], 70+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602", 1, (220,220,220))
            screen.blit(label, (65+currentPlayer.corner[0], 140+currentPlayer.corner[1]))


        #-------scorecard header-------
        screen.blit(currentPlayer.profile, (10+currentPlayer.corner[0], 10+currentPlayer.corner[1])) #profile picture

        color = (220,220,220)
        if currentPlayer.place <=3:
            color = (239,195,0)
        nameRender = getFont(24).render(str(currentPlayer.nameCaseSensitive), 1, color)
        placeRender = getFont(45).render(str(currentPlayer.place), 1, color)

        screen.blit(nameRender, (75+currentPlayer.corner[0], 22+currentPlayer.corner[1])) #name

        if currentPlayer.place > 9:
            screen.blit(placeRender, (260+currentPlayer.corner[0], 8+currentPlayer.corner[1]))
        else:
            screen.blit(placeRender, (280+currentPlayer.corner[0], 8+currentPlayer.corner[1]))


    pygame.display.flip()
    return screen