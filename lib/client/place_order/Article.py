import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Farm_model:
	
	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.order = None
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.order = self.chat.user.order