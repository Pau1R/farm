from lib.Database import Database
from lib.equipment.Equipment import Equipment
from lib.Chat import Chat
from datetime import date
import re
from lib.Msg import Message
from lib.order.Order import Order
from lib.order.Logic import Order_logic
from lib.order.gcode.Gcode import Gcode
from lib.order.gcode.Logic import Gcode_logic
from lib.equipment.printer.Logic import Printer_logic
from lib.request.Logic import Request_logic
from lib.setting.Setting import Setting
from lib.Clicker import Clicker
import jsonpickle
from datetime import date
from lib.Functions import Functions

from lib.Test import Test

class App:
	chats = []

	def __init__(self, bot, conf):
		self.orders = []
		self.gcodes = []
		self.requests = []
		
		self.bot = bot
		self.conf = conf
		self.equipment = Equipment()
		self.db = Database(self)
		self.equipment.init(self, self.db)
		self.db.get_chats()
		self.db.get_orders()
		self.db.get_gcodes()
		self.setting = Setting(self)
		self.order_logic = Order_logic(self)
		self.gcode_logic = Gcode_logic(self)
		self.clicker = Clicker(self)
		self.printer_logic = Printer_logic(self)
		self.request_logic = Request_logic(self)
		self.functions = Functions()
		
		# test = Test(self)

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
		chat = Chat(self, int(message.user_id), message.user_name, False, date.today())
		self.chats.append(chat)
		self.db.create_chat(chat)
		return chat

	def get_chat(self, user_id):
		for chat in self.chats:
			if chat.user_id == int(user_id):
				return chat

	def get_chats(self, roles):
		if type(roles) == str:
			roles = [roles]
		chats = []
		for chat in self.chats:
			if chat.is_employee:
				for role in roles:
					if role in chat.user.roles:
						chats.append(chat)
		return chats

	def chat_payed(self, user_id, amount):
		chat = self.get_chat(user_id)
		chat.user.money_payed += amount
		self.db.update_chat(chat)

	def orders_append(self, order):
		order.id = self.get_next_free_id(self.orders)
		self.orders.append(order)

	def gcodes_append(self, gcode):
		gcode.id = self.get_next_free_id(self.gcodes)
		self.gcodes.append(gcode)

	def get_next_free_id(self, list_):
		ids = []
		for element in list_:
			ids.append(int(element.id))
		ids.sort()
		ids = list(dict.fromkeys(ids))
		id = 1
		for elem in ids:
			if elem == id:
				id += 1
			else:
				break
		return id

	def telethon_new_message(self, event):
		print('app.py telethon_new_message')
		text = event.message.message
		chat_id = int(event.message.peer_id.user_id)
		chat_id = 240044026  # TODO: remove for production!
		if not ('Перевод' in text and chat_id == 240044026):
			return

		sender = re.search(r'от ([А-Яа-яЁё]+\s[А-Яа-яЁё]+\.)', text)
		sender = sender.group(1) if sender else ''
		
		amount = re.search(r'Перевод (\d[\d ]*)р', text)
		amount = int(amount.group(1).replace(' ', '') if amount else '0')

		pay_code = re.search(r'«.*?(\d+).*?»', text)
		pay_code = int(pay_code.group(1) if pay_code else '0')

		order = self.order_logic.get_order_by_pay_code(pay_code)
		if order:
			order.payed(amount)
		else:
			for admin in self.get_chats('Администратор'):
				admin.user.admin.show_unmatched_payment(sender, amount, pay_code)

# app structure for buttons:
# 1 client 
#	1 their_model
#	2 client_color
#   3 order_GUI
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
#	  9 setting
#     10 requests
#	3 Operator
#	4 Designer
#	  1 Validate
#	5 Delivery

# TODO:
# - admin: view all orders, clients (their name) and client orders, tell info to client
