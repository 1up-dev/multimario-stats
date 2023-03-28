import settings
from scoreboard import slots

def sort(playerLookup):
    # sorting runners for display
    sortedRacers = []
    all_racers_done = True
    for key in list(playerLookup.keys()):
        if playerLookup[key].status == "live":
            all_racers_done = False
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
                if playerLookup[key].score > playerLookup[racer].score:
                    sortedRacers.insert(index, key)
                    break
                elif index == len(sortedRacers)-1:
                    sortedRacers.append(key)
                    break
    settings.stopTimer = all_racers_done
    
    # place & slot assignments
    slot = 0
    page = 0
    for index, racer in enumerate(sortedRacers):
        current = playerLookup[racer]

        # slot assignment
        current.corner = slots[slot]
        current.page = page
        if 0 <= slot <= 2:
            current.page = -1 # pin top 3
        slot += 1
        if slot > 27:
            slot = 3
            page += 1
        
        # place assignment
        if index == 0:
            current.place = 1
            continue
        previous = playerLookup[sortedRacers[index-1]]
        if current.status != 'done':
            if current.score == previous.score:
                current.place = previous.place
                continue
        current.place = index+1
