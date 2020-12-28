import datetime

def init():
    global startTime
    startTime = datetime.datetime.now()
    global doQuit
    doQuit = False
    global redraw
    redraw = True