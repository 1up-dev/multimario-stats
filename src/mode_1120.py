import pygame
import math
import sort

star  = pygame.image.load('./resources/star.png')
shine = pygame.image.load('./resources/shine.png')
moon = pygame.image.load('./resources/moon.png')
background = pygame.image.load('./resources/background.png')
sm64BG = pygame.image.load('./resources/sm64.png')
smsBG = pygame.image.load('./resources/sms.png')
smoBG = pygame.image.load('./resources/smo.png')
finishBG = pygame.image.load('./resources/finish-sm64.png')

total = 1120

#slots = [
    #(10,290),(407,290),(804,290),(1201,290),
    #(10,495),(407,495),(804,495),(1201,495),
    #(10,700),(407,700),(804,700),(1201,700),(1600,900)
#] #387 x 175 scorecards
slots = [
             (407,290),(804,290),
    (200,495),(607,495),(1014,495),
    (200,700),(607,700),(1014,700),(1600,900)
] #387 x 175 scorecards

def collected(tempStars):
    game=""
    buffer=""
    noun=""
    if tempStars <= 880:
        game="Super Mario Odyssey"
        noun="Moon"
    elif tempStars <= 1000:
        game="Super Mario Sunshine"
        tempStars -= 880
        noun="Shine"
    elif tempStars <= 1120:
        game="Super Mario 64"
        tempStars -= 1000
        noun="Star"
    if tempStars != 1:
        buffer = "s"
    return " now has " + str(tempStars) + " "+ noun+buffer + " in " + game + "."

def getFont(size):
    return pygame.font.Font("./resources/Lobster 1.4.otf", size)

def draw(screen, playerLookup):
    screen.blit(pygame.transform.scale(background, (1600,900)), (0,0))
    sortedRacers = sort.sort(playerLookup)

    #1120 fall 2020 slots
    racerIndex=0
    for s in range(0,len(sortedRacers)):
        if s==-1: #leaving empty slots for spacing
            pass
        elif racerIndex < 8:
            playerLookup[sortedRacers[racerIndex]].corner = slots[s]
            racerIndex+=1
        else:
            playerLookup[sortedRacers[racerIndex]].corner = [1600, 900]
            racerIndex+=1

    #-----------scorecard drawing------------
    for key in playerLookup:
        currentPlayer = playerLookup[key]
        corner = currentPlayer.corner
        pygame.draw.rect(screen, (25, 25, 25), [corner[0]-3, corner[1]-3, 393, 181])

        score = currentPlayer.collects
        if currentPlayer.status == "live":
            smocount = 0
            smscount = 0
            sm64count = 0
            # smgcount = 0
            # smg2count = 0
            if score < 880:
                screen.blit(smoBG, (corner[0], corner[1]))
                smocount = score
            elif score < 1000:
                screen.blit(smsBG, (corner[0], corner[1]))
                smocount = 880
                smscount = score-880
            elif score < 1120:
                screen.blit(sm64BG, (corner[0], corner[1]))
                smocount = 880
                smscount = 120
                sm64count = score-1000

            smallBar = 136
            largeBar = 322
            barHeight = 20
            smolength = math.floor((smocount/880)*largeBar)
            smslength = math.floor((smscount/120)*largeBar)
            sm64length = math.floor((sm64count/120)*largeBar)

            s = pygame.Surface((largeBar+4, barHeight), pygame.SRCALPHA)
            s.fill((80,80,80,192))
            screen.blit(s, (40+corner[0], 80+corner[1]))
            screen.blit(s, (40+corner[0], 112+corner[1]))
            screen.blit(s, (40+corner[0], 144+corner[1]))
            if score > 0:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 80+corner[1]+2, smolength, barHeight-4])
            if score > 880:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 112+corner[1]+2, smslength, barHeight-4])
            if score > 1000:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 144+corner[1]+2, sm64length, barHeight-4])

            # Render per-game star counts
            if smocount > 67:
                label = getFont(18).render(str(smocount), 1, (60,60,60))
                screen.blit(label, (45+corner[0], 79+corner[1]))
            else:
                label = getFont(18).render(str(smocount), 1, (220,220,220))
                screen.blit(label, (45+smolength+corner[0], 79+corner[1]))
            if smscount > 5:
                label = getFont(18).render(str(smscount), 1, (60,60,60))
                screen.blit(label, (45+corner[0], 111+corner[1]))
            else:
                label = getFont(18).render(str(smscount), 1, (220,220,220))
                screen.blit(label, (45+smslength+corner[0], 111+corner[1]))
            if sm64count > 5:
                label = getFont(18).render(str(sm64count), 1, (60,60,60))
                screen.blit(label, (45+corner[0], 143+corner[1]))
            else:
                label = getFont(18).render(str(sm64count), 1, (220,220,220))
                screen.blit(label, (45+sm64length+corner[0], 143+corner[1]))


            #------------individual game scores & icons--------------
            screen.blit(moon, (7+corner[0], 73+corner[1]) )
            # label = getFont(18).render(str(smocount), 1, smocolor)
            # screen.blit(label, (45+corner[0], 79+corner[1]))

            screen.blit(shine, (6+corner[0], 103+corner[1]) )
            # label = getFont(18).render(str(smscount), 1, smscolor)
            # screen.blit(label, (45+corner[0], 111+corner[1]))

            screen.blit(star, (6+corner[0], 137+corner[1]) )
            # label = getFont(18).render(str(sm64count), 1, sm64color)
            # screen.blit(label, (45+corner[0], 143+corner[1]))

        elif currentPlayer.status == "done":    #shows done tag
            screen.blit(finishBG, (playerLookup[key].corner[0], playerLookup[key].corner[1]))
            doneTag = getFont(70).render("Done!", 1, (220,220,220))
            screen.blit(doneTag, (120+currentPlayer.corner[0], 65+currentPlayer.corner[1]))

            label = getFont(24).render(str("Final Time: {0}".format(currentPlayer.completionTime)), 1, (220,220,220))
            screen.blit(label, (100+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "quit":    #shows quit tag
            quitTag = getFont(70).render("Quit", 1, (255, 0, 0))
            screen.blit(quitTag, (130+currentPlayer.corner[0], 55+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/"+str(total)+" in "+currentPlayer.completionTime, 1, (220,220,220))
            screen.blit(label, (50+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "disqualified":    #shows disqualified tag
            forfeitTag = getFont(50).render("Disqualified", 1, (255, 0, 0))
            screen.blit(forfeitTag, (80+currentPlayer.corner[0], 70+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/"+str(total), 1, (220,220,220))
            screen.blit(label, (100+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "noshow":    #shows no-show tag
            forfeitTag = getFont(50).render("No-Show", 1, (255, 0, 0))
            screen.blit(forfeitTag, (110+currentPlayer.corner[0], 70+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/"+str(total), 1, (220,220,220))
            screen.blit(label, (100+currentPlayer.corner[0], 140+currentPlayer.corner[1]))


        #-------scorecard header-------
        screen.blit(currentPlayer.profile, (10+currentPlayer.corner[0], 10+currentPlayer.corner[1])) #profile picture

        if currentPlayer.place <=3:
            nameRender = getFont(28).render(str(currentPlayer.nameCaseSensitive), 1, (239,195,0))
            placeRender = getFont(45).render(str(currentPlayer.place), 1, (239,195,0))
        else:
            nameRender = getFont(28).render(str(currentPlayer.nameCaseSensitive), 1, (220,220,220))
            placeRender = getFont(45).render(str(currentPlayer.place), 1, (200,200,200))

        screen.blit(nameRender, (80+currentPlayer.corner[0], 20+currentPlayer.corner[1])) #name

        if currentPlayer.place > 9:
            screen.blit(placeRender, (335+currentPlayer.corner[0], 8+currentPlayer.corner[1]))
        else:
            screen.blit(placeRender, (350+currentPlayer.corner[0], 8+currentPlayer.corner[1]))


    pygame.display.flip()
    return screen
