import sys
import time
import asyncio
from threading import Thread

try:
    import launchpad_py as launchpad
except ImportError:
    try:
        import launchpad
    except ImportError:
        sys.exit("ERROR: loading launchpad.py failed")

import random

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
import tornado.web

class WSHandler(tornado.websocket.WebSocketHandler):

    def write_file(self, msg):
        self.logfile.write(msg + "\n")

    def initialize(self, lp):
        self.lp = lp
        self.logfile = open("C:/Users/Titan Robotics/Documents/NovationLaunchpad/lp_log.txt", "w")

        self.write_file("initialized")

    def open(self):
        self.callback = PeriodicCallback(self.send_hello, 1)
        self.callback.start()

        self.write_file("remote ip: " + self.request.remote_ip)
        self.write_file("req. uri: " + self.request.uri)
        self.write_file("full url: " + self.request.full_url())

    def send_hello(self):
        events = self.lp.ButtonStateXY()
        if events:
            self.write_file("sending " + str(events))
            self.write_message(str(events[0]) + ":" + \
                               str(events[1]) + ":" + \
                               str(events[2]))

    def on_message(self, message):
        pass

    def on_close(self):
        self.callback.stop()

        self.logfile.close()

def hsv_to_rgb(h, s, v):
    if s == 0.0: v*=255; return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

def main():

    # 60, 23, 10

    # some basic info
    print( "\nRunning..." )
    print( " - Python " + str( sys.version.split()[0] ) )

##    ledCodes = [[1,1,0,0,0,0,5,5],
##                [90,90,0,82,82,0,0,9],
##                [90,90,0,82,82,0,5,5],
##                [0,0,0,0,0,0,0,13],
##                [126,126,0,109,109,0,9,9],
##                [126,126,0,109,109,0,0,82],
##                [0,0,0,0,0,13,13,90],
##                [9,9,0,13,13,0,21,21]]

    # colors
    red =       (255, 0, 0)
    green =     (0, 255, 0)
    blue =      (0, 0, 255)
    yellow =    (255, 255, 0)
    cyan =      (0, 255, 255)
    magenta =   (255, 0, 255)
    white =     (255, 255, 255)

    ledCodes = [
        [red, red, red, white, white, white, white, white, cyan],
        [red, red, *[hsv_to_rgb((i+1)/5., 1, 1) for i in range(5)], cyan, cyan],
        [red, white, white, white, white, white, white, white, cyan],
        [*[hsv_to_rgb(i/8., 1, 1) for i in range(9)]],
        [magenta, magenta, white, white, green, green, white, white, white],
        [magenta, magenta, white, blue, blue, blue, blue, blue, blue],
        [white, white, white, white, white, white, white, white, blue],
        [yellow, yellow, yellow, yellow, red, red, green, green, blue],
        [red, red, red, red, yellow, yellow, cyan, cyan, blue]
    ]

    

    # create an instance
    lp = launchpad.LaunchpadLPX()

    # open the first Launchpad LPX
    if lp.Open( 0 ):
        print( " - Launchpad X: OK" )
    else:
        print( " - Launchpad X: ERROR" )
        return

    # Clear the buffer because the Launchpad remembers everything
    lp.ButtonFlush()
    
    for i in range(len(ledCodes)):
        for j in range(len(ledCodes[i])):
            lp.LedCtrlXY(i, j, *ledCodes[j][i])

    # buttonThread = Thread(target = process_buttons, args = (lp, ))
    # buttonThread.start()

    print("Starting...")

    application = tornado.web.Application([(r'/', WSHandler,{"lp": lp})],)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(5802)
    tornado.ioloop.IOLoop.instance().start()

    # close this instance
    print( " - More to come, goodbye...\n" )
    lp.Close()

    
if __name__ == '__main__':
    main()


