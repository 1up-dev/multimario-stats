import settings

def sort(playerLookup):
    # sorting runners for display
    sortedRacers = []
    all_racers_done = True
    for key in playerLookup:
        if len(sortedRacers) == 0:
            sortedRacers.append(key)
        elif playerLookup[key].status == 'done':
            for index, racer in enumerate(sortedRacers):
                if playerLookup[racer].status != 'done':
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
                #set all_racers_done flag to False if any racer is live
                if playerLookup[key].status == "live":
                    all_racers_done = False
                if playerLookup[key].score > playerLookup[racer].score:
                    sortedRacers.insert(index, key)
                    break
                elif index == len(sortedRacers)-1:
                    sortedRacers.append(key)
                    break
    if all_racers_done:
        settings.stopTimer = True
    else:
        settings.stopTimer = False

    # place number assignments
    for index, racer in enumerate(sortedRacers):
        if index == 0:
            playerLookup[racer].place = 1
            continue
        current = playerLookup[racer]
        previous = playerLookup[sortedRacers[index-1]]
        if current.status != 'done':
            if current.score == previous.score:
                current.place = previous.place
            else:
                playerLookup[racer].place = index+1
        else:
            playerLookup[racer].place = index+1

    return sortedRacers
