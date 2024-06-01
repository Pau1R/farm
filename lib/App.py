from lib.Database import Database
from lib.equipment.Equipment import Equipment
from lib.Chat import Chat
from datetime import date
from lib.Msg import Message
from lib.client.Order import Order
from lib.client.Order_logic import Order_logic
from lib.Test import Test
from lib.Settings import Settings
from lib.Clicker import Clicker
import jsonpickle
from datetime import date
from lib.Functions import Functions

class App:
	bot = None
	conf = None
	db = None
	equipment = None
	settings = None
	orders = []
	functions = Functions()
	clicker = None

	chats = []
	chat = None
	count = 0
	last_check_date = None

	order_logic = None

	def __init__(self, bot, conf):
		self.bot = bot
		self.conf = conf
		self.equipment = Equipment()
		self.db = Database(self)
		self.equipment.init(self, self.db)
		self.db.get_chats()
		self.db.get_orders()
		self.settings = Settings(self)
		self.order_logic = Order_logic(self)
		self.clicker = Clicker(self)
		# test = Test(self.db, self)

	def new_message(self, message):
		self.clicker.click()
		print('app.py new_message')
		message = Message(message)
		self.chat = None
		user_id = int(message.user_id)

		for chat in self.chats:
			if chat.user_id == user_id:
				self.chat = chat
				self.chat.last_access_date = date.today()
		if self.chat == None:
			self.chat = self.create_chat(message)
		self.chat.new_message(message)

	def create_chat(self, message):
		chat = Chat(self, int(message.user_id), False, date.today())
		self.chats.append(chat)
		self.db.create_chat(chat)
		return chat

	def get_chat(self, user_id):
		for chat in self.chats:
			if chat.user_id == int(user_id):
				return chat

# app structure for buttons:
# 1 client 
#	1 client_model
#	2 client_color
#   3 client_order
#   4 client_info
# 1 Employee
#	1 Owner
#	2 Admin
#     1 container
#     2 dryer
#     3 extruder
#     4 location
#     5 printer
#     6 spool
#     7 color
#     8 surface
#	  9 settings
#	3 Operator
#	4 Designer
#	  1 Validate
#	5 Delivery
