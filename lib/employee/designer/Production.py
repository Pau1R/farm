import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.Texts import Texts

class Production:
	address = ''

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''

	order = None
	
	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		function = message.function
		if message.data_special_format:
			if self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				if function == '2':
					self.process_order()
				if function == '3':
					self.process_reject()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.context = ''
		text = f'Выберите заказ'
		logic = self.app.order_logic
		orders = logic.get_orders_by_type(self.app.orders, 'production')
		orders = logic.get_orders_by_status(orders, 'validate')
		orders = logic.get_orders_by_user_id(orders, self.chat.user_id)
		buttons = logic.convert_orders_to_buttons(orders)
		if buttons:
			buttons.extend(['Назад'])
			self.GUI.tell_buttons(text, buttons, buttons, 1, 0)
		else:
			self.chat.user.designer.first_message(self.message)

	def show_order(self):
		# TODO: add ability to change order values, e.g. add stl file, change weight, etc.

		text = f'Заказ № {self.order.id} "{self.order.name}" \nДата добавления: {self.app.functions.russian_date(self.order.date)}'
		text += f'\nВес одного экземпляра: {self.order.weight} грамм'
		if self.order.quantity > 1:
			text += f'\nКоличество экземпляров: {self.order.quantity}'
		if self.order.comment:
			text += f'\nКомментарий клиента: {self.order.comment}'
		text += f'\nДополнительная информация: {self.order.quality}'
		buttons = []
		if self.order.assigned_designer_id:
			buttons.append(['Перевести в чат', 'chat'])
			buttons.append(['Отказать','reject'])
		else:
			buttons.append(['Взять в работу', 'take'])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 2, self.order.id)

	def show_reject(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell_buttons('Напишите причину отказа', [['Не уточнять причину', 'none'], 'Назад'], [], 3, self.order.id)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.chat.user.designer.last_data = ''
			self.chat.user.designer.first_message(self.message)
		else:
			for order in self.app.orders:
				if order.id == int(self.message.btn_data):
					self.order = order
					self.show_order()

	def process_order(self):
		if self.message.btn_data == 'Назад':
			self.order = None
			self.show_top_menu()
		elif self.message.btn_data == 'take':
			self.order.assigned_designer_id = self.chat.user_id
			self.app.db.update_order(self.order)
			self.show_order()
		elif self.message.btn_data == 'chat':
			chat = self.app.get_chat(self.order.user_id)
			chat.user.show_redirect_to_chat(self.order)
			self.order.quality += '\nЗаказ переведен в чат'
			self.show_order()
		elif self.message.btn_data == 'reject':
			self.show_reject()

	def process_reject(self):
		self.chat.context = ''
		data = self.message.btn_data
		if data == 'Назад':
			self.show_order()
			return
		elif data == 'none':
			reason = ''
		else:
			reason = self.message.text
		user = self.get_user(self.order.user_id)
		user.order_GUI.show_rejected_by_designer(self.order, reason)
		self.app.orders.remove(self.order)
		self.app.db.remove_order(self.order)
		self.order == None
		self.show_top_menu()