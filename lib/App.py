from lib.Database import Database
from lib.equipment.Equipment import Equipment
from lib.Chat import Chat
from datetime import date
from lib.Msg import Message
from lib.client.Order import Order
from lib.Test import Test
from lib.Settings import Settings
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

	chats = []
	chat = None
	count = 0
	last_check_date = None

	def __init__(self, bot, conf):
		self.bot = bot
		self.conf = conf
		self.equipment = Equipment()
		self.db = Database(self)
		self.equipment.init(self, self.db)
		self.db.get_chats()
		self.db.get_orders()
		self.settings = Settings(self)
		# test = Test(self.db, self)

	def new_message(self, message):
		print('app.py new_message')
		message = Message(message)
		self.chat = None
		user_id = message.user_id

		for obj in self.chats:
			if obj.user_id == user_id:
				self.chat = obj
				self.chat.last_access_date = date.today()
		if self.chat == None:
			self.chat = self.create_chat(message)
		self.chat.new_message(message)

		self.remove_inactive_chats()

	def create_chat(self, message):
		chat = Chat(self, message.user_id, False, date.today())
		self.chats.append(chat)
		self.db.create_chat(chat)
		return chat

	def remove_inactive_chats(self):  # TODO: also remove forgotten and unpaid orders
		if self.count < 100:  
			self.count += 1
			return
		self.count = 0
		today = date.today()
		if today != self.last_check_date: # run check once a day
			self.last_check_date = today
			for obj in self.chats:
				if not obj.is_employee:
					period = (today - obj.last_access_date).days
					if period < 30:
						break
					elif period < 60:
						for order in self.orders:
							if order.user_id == obj.user_id:
								break
					chats.remove(obj)


# app structure for buttons:
# 1 client 
#	1 client_model
#	2 client_color
#	3 client_logic
#   4 client_order
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


# TODO: Designer_validate.py 1, Client_color.py 1, client_order.py, client wait for specific material

# preordered spools: status: ordered, in_stock; delivery_date_estimate
