from lib.Database import Database
from lib.equipment.Equipment import Equipment
from lib.Chat import Chat
from datetime import date
from lib.Msg import Message
from lib.client.Order import Order
from lib.Test import Test
import jsonpickle
from datetime import date

class App:
	bot = None
	conf = None
	db = None
	equipment = None
	orders = []

	chats = []
	chat = None

	# settings:
	support_remove_price = 10
	petg_density = 1.25

	# count = 0
	# last_check_date = None

	def __init__(self, bot, conf):
		self.bot = bot
		self.conf = conf
		self.equipment = Equipment()
		self.db = Database(self)
		self.equipment.init(self.db)
		self.db.get_chats()
		self.db.get_orders()
		# test = Test(self.db, self)

	def new_message(self, message):                # find chat object and tell him to process incoming message
		print('app.py new_message')
		message = Message(message)
		self.chat = None
		user_id = message.user_id

		for obj in self.chats:
			if obj.user_id == user_id:
				self.chat = obj
		if self.chat == None:
			self.chat = self.create_chat(message)

		self.chat.new_message(message)                  # process message data

		# self.remove_inactive_chats()

	def create_chat(self, message):
		chat = Chat(self, message.user_id, False, date.today())
		self.chats.append(chat)
		self.db.create_chat(chat)
		return chat

	def remove_inactive_chats(self):  # every 100 messages check if date has changed
		if self.count < 100:  
			self.count += 1
			return
		self.count = 0
		today = date.today()
		if today != self.last_check_date: # if data has changed check chats last activity date
			self.last_check_date = today
			for obj in self.chats:
				if (today - obj.last_access_date).days >= 10: # if chat hasn't activity last 10 days, remove object
					chats.remove(obj)