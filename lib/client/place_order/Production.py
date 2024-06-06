import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Production:
	address = ''

	app = None
	chat = None
	order = None
	GUI = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.order = self.chat.user.order