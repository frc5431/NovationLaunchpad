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

	def initialize(self, lp):
		self.lp = lp

	def open(self):
		self.callback = PeriodicCallback(self.send_hello, 1)
		self.callback.start()

	def send_hello(self):
		events = self.lp.ButtonStateXY()
		if events:
			print("sending")
			self.write_message(str(events[0]) + ":" + str(events[1]) + ":" + str(events[2]))

	def on_message(self, message):
		pass

	def on_close(self):
		self.callback.stop()


def main():

	# 60, 23, 10

	# some basic info
	print( "\nRunning..." )
	print( " - Python " + str( sys.version.split()[0] ) )

	ledCodes = [[1,1,1,1,0,0,0,5,5],
				[90,90,0,82,82,0,0,0,9],
				[90,90,0,82,82,0,5,5,0],
				[0,0,0,0,0,0,0,0,13],
				[126,126,0,109,109,0,9,9,0],
				[126,126,0,109,109,0,0,0,0],
				[0,0,0,0,0,0,13,13,5],
				[9,9,0,13,13,0,0,0,0],
				[9,9,0,13,13,0,21,21,21]]

	# create an instance
	lp = launchpad.LaunchpadMk2()

	# open the first Launchpad Mk2
	if lp.Open( 0, "mk2" ):
		print( " - Launchpad Mk2: OK" )
	else:
		print( " - Launchpad Mk2: ERROR" )
		return

	# Clear the buffer because the Launchpad remembers everything
	lp.ButtonFlush()
	
	for i in range(9):
		for j in range(9):
			lp.LedCtrlXYByCode(i, j, ledCodes[j][i])

	# buttonThread = Thread(target = process_buttons, args = (lp, ))
	# buttonThread.start()

	application = tornado.web.Application([(r'/', WSHandler,{"lp": lp})],)

	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(9001)
	tornado.ioloop.IOLoop.instance().start()

	# close this instance
	print( " - More to come, goodbye...\n" )
	lp.Close()

	
if __name__ == '__main__':
	main()


