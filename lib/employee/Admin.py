import sys
sys.path.append('../lib')
# from lib.Msg import Message
from lib.Gui import Gui
from lib.equipment.Equipment import Equipment
from lib.equipment.container.GUI import ContainerGUI
from lib.equipment.dryer.GUI import DryerGUI
from lib.equipment.extruder.GUI import ExtruderGUI
from lib.equipment.zone.GUI import ZoneGUI
from lib.equipment.printer_type.GUI import Printer_typeGUI
from lib.equipment.printer.GUI import PrinterGUI
from lib.equipment.spool.GUI import SpoolGUI
from lib.equipment.color.GUI import ColorGUI
from lib.equipment.Bed.GUI import BedGUI
from lib.setting.GUI import SettingsGUI
from lib.order.GUI import Order_GUI
from lib.request.GUI import RequestGUI

class Admin:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.message = None
		self.address = address
		self.GUI = Gui(app, chat, address)

		self.containerGUI = ContainerGUI(app, chat, address + '/1')
		self.dryerGUI = DryerGUI(app, chat, address + '/2')
		self.extruderGUI = ExtruderGUI(app, chat, address + '/3')
		self.zoneGUI = ZoneGUI(app, chat, address + '/4')
		self.printer_typeGUI = Printer_typeGUI(app, chat, address + '/5')
		self.printerGUI = PrinterGUI(app, chat, address + '/6')
		self.spoolGUI = SpoolGUI(app, chat, address + '/7')
		self.colorGUI = ColorGUI(app, chat, address + '/8')
		self.bedGUI = BedGUI(app, chat, address + '/9')
		self.settingsGUI = SettingsGUI(app, chat, address + '/10')
		
		self.order_GUI = Order_GUI(app, chat, address + '/11')
		self.requestGUI = RequestGUI(app, chat, address + '/12')

		self.client = None

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				self.containerGUI.new_message(message)
			elif file == '2':
				self.dryerGUI.new_message(message)
			elif file == '3':
				self.extruderGUI.new_message(message)
			elif file == '4':
				self.zoneGUI.new_message(message)
			elif file == '5':
				self.printer_typeGUI.new_message(message)
			elif file == '6':
				self.printerGUI.new_message(message)
			elif file == '7':
				self.spoolGUI.new_message(message)
			elif file == '8':
				self.colorGUI.new_message(message)
			elif file == '9':
				self.bedGUI.new_message(message)
			elif file == '10':
				self.settingsGUI.new_message(message)
			elif file == '11':
				self.order_GUI.new_message(message)
			elif file == '12':
				self.requestGUI.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				elif function == '2':
					self.process_orders()
				elif function == '3':
					self.process_orders_by_type()
				elif function == '4':
					self.process_clients()
				elif function == '5':
					self.process_client()
				elif function == '6':
					self.process_message()
				elif function == '7':
					self.process_equipment()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'Здравствуйте, Администратор ' + self.chat.user_name
		items = self.app.order_logic.get_orders_by_status(self.app.orders, 'item_received') # TODO: 'waiting_for_design' status after item is at designer
		if items:
			text += f'\n\nНеобходимо забрать предметы из доставки: {len(items)} шт.'
		buttons = ['Заказы', 'Клиенты', 'Оборудование', 'Настройки']
		if len(self.app.requests):
			buttons.append(['Обращения в поддержку', 'request'])
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_orders(self):
		orders = self.app.orders.copy()
		data = self.app.data
		text = 'Все активные заказы'
		removed = []
		buttons_2 = []
		if len(orders) > 10:
			quantities = {}
			for order in orders:
			   quantities[order.type] = quantities.get(order.type, 0) + 1
			quantities = dict(sorted(quantities.items(), key=lambda item: item[1], reverse=True))
			total_orders = len(orders)
			for order_type, count in quantities.items():
				if total_orders + len(buttons_2) >= 10:
					orders = [order for order in orders if order.type != order_type]
					buttons_2.append([data.types[order_type], order_type])
					removed.append(order_type)
				else:
					break
				total_orders -= count
		buttons = []
		for order in orders:
			chat = self.app.get_chat(order.user_id)
			buttons.append([f'{order.id}: {order.name} ({chat.user_name})', order.id])
		buttons.extend(buttons_2)
		if not buttons:
			self.show_top_menu()
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'], 2, 0)

	def show_orders_by_type(self, type_):
		data = self.app.data
		text = f'Заказы "{data.types[type_]}"'
		buttons = []
		for order in self.app.orders:
			if order.type == type_:
				buttons.append([f'{order.id}: {order.name}', order.id])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 3, 0)

	def show_clients(self):
		text = 'Клиенты активных заказов'
		buttons = []
		unique_chats = set()
		for order in self.app.orders:
			chat = self.app.get_chat(order.user_id)
			if chat.user_id not in unique_chats:
				buttons.append([chat.user_name, chat.user_id])
				unique_chats.add(chat.user_id)
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'], 4, 0)

	def show_client(self):
		chat = self.client
		text = f'Имя: {chat.user_name}\n'
		text += f'Id: {chat.user_id}\n'
		text += f'Дата последней активности: {self.app.functions.russian_date(chat.last_access_date)}\n'
		text += f'Код оплаты: {chat.user.payId}\n'
		text += f'Оплачено клиентом: {int(chat.user.money_payed)} рублей\n'
		text += f'Отмененных заказов: {chat.user.orders_canceled}\n'
		text += f'Дата последней блокировки: {self.app.functions.russian_date(chat.user.limit_date)}\n\n'
		orders = self.app.order_logic.get_client_orders(chat.user_id)
		if orders:
			text += 'Активные заказы:\n'
			for order in orders:
				text += f'{order.id}: {order.name}\n'
		buttons = [['Написать сообщение','message']]
		if False: # FUTURE_TODO: manage history
			buttons.append(['Завершенные заказы','finished'])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'], 5, 0)

	def show_message(self):
		self.chat.set_context(self.address, 6)
		text = 'Напишите сообщение клиенту'
		self.GUI.tell(text)

	def show_equipment(self):
		buttons = ['Локации', 'Типы принтеров', 'Принтеры', 'Экструдеры', 'Поверхности', 'Сушилки', 'Катушки', 'Цвета', 'Ящики']
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите оборудование', buttons, ['Назад'], 7, 0)

	def show_unmatched_payment(self, sender, amount, pay_code):
		text = 'Поступил некорректный платеж.\n\n'
		text += f'Отправитель: {sender}\n'
		text += f'Сумма: {amount}\n'
		text += f'Код платежа: {pay_code}'
		self.GUI.tell_permanent(text)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		if data == 'Заказы':
			self.show_orders()
		if data == 'Клиенты':
			self.show_clients()
		elif data == 'Оборудование':
			self.show_equipment()
		elif data == 'Настройки':
			self.settingsGUI.last_data = ''
			self.settingsGUI.first_message(self.message)
		elif data == 'request':
			self.requestGUI.last_data = ''
			self.requestGUI.first_message(self.message)

	def process_orders(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_top_menu()
		elif data in ['stl','link','sketch','item','production']:
			self.show_orders_by_type(data)
		else:
			self.message.instance_id = self.message.btn_data
			self.order_GUI.last_data = ''
			self.order_GUI.first_message(self.message)

	def process_orders_by_type(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_orders()
		else:
			self.message.instance_id = self.message.btn_data
			self.order_GUI.last_data = ''
			self.order_GUI.first_message(self.message)

	def process_clients(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_top_menu()
		else:
			self.client = self.app.get_chat(data)
			self.show_client()

	def process_client(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_clients()
		if data == 'message':
			self.show_message()
		if data == 'finished':
			x = ''

	def process_message(self):
		self.chat.context = ''
		text = f'Сообщение от администратора: {self.message.text}'
		self.GUI.tell_id(self.client.user_id, text)

	def process_equipment(self):
		if self.message.btn_data == 'Ящики':
			self.containerGUI.last_data = ''
			self.containerGUI.first_message(self.message)
		elif self.message.btn_data == 'Сушилки':
			self.dryerGUI.last_data = ''
			self.dryerGUI.first_message(self.message)
		elif self.message.btn_data == 'Экструдеры':
			self.extruderGUI.last_data = ''
			self.extruderGUI.first_message(self.message)
		elif self.message.btn_data == 'Локации':
			self.zoneGUI.last_data = ''
			self.zoneGUI.first_message(self.message)
		elif self.message.btn_data == 'Типы принтеров':
			self.printer_typeGUI.last_data = ''
			self.printer_typeGUI.first_message(self.message)
		elif self.message.btn_data == 'Принтеры':
			self.printerGUI.last_data = ''
			self.printerGUI.first_message(self.message)
		elif self.message.btn_data == 'Катушки':
			self.spoolGUI.last_data = ''
			self.spoolGUI.first_message(self.message)
		elif self.message.btn_data == 'Цвета':
			self.colorGUI.last_data = ''
			self.colorGUI.first_message(self.message)
		elif self.message.btn_data == 'Поверхности':
			self.bedGUI.last_data = ''
			self.bedGUI.first_message(self.message)
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()