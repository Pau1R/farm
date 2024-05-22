import sys
sys.path.append('../lib')
# from lib.Msg import Message
from lib.Gui import Gui
from lib.Texts import Texts
from lib.equipment.Equipment import Equipment
from lib.equipment.GUI.Container import ContainerGUI
from lib.equipment.GUI.Dryer import DryerGUI
from lib.equipment.GUI.Extruder import ExtruderGUI
from lib.equipment.GUI.Location import LocationGUI
from lib.equipment.GUI.Printer_type import Printer_typeGUI
from lib.equipment.GUI.Printer import PrinterGUI
from lib.equipment.GUI.Spool import SpoolGUI
from lib.equipment.GUI.Color import ColorGUI
from lib.equipment.GUI.Surface import SurfaceGUI
from lib.employee.SettingsGUI import SettingsGUI
from lib.client.Client_order import Client_order

class Admin:
	address = '1/2'

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''
	texts = None

	containerGUI = None
	dryerGUI = None
	extruderGUI = None
	locationGUI = None
	printer_typeGUI = None
	printerGUI = None
	spoolGUI = None
	colorGUI = None
	surfaceGUI = None
	settingsGUI = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address)

		self.containerGUI = ContainerGUI(app, chat)
		self.dryerGUI = DryerGUI(app, chat)
		self.extruderGUI = ExtruderGUI(app, chat)
		self.locationGUI = LocationGUI(app, chat)
		self.printer_typeGUI = Printer_typeGUI(app, chat)
		self.printerGUI = PrinterGUI(app, chat)
		self.spoolGUI = SpoolGUI(app, chat)
		self.colorGUI = ColorGUI(app, chat)
		self.surfaceGUI = SurfaceGUI(app, chat)
		self.settingsGUI = SettingsGUI(app, chat)

		self.client_order = Client_order(app, chat, '1/2/11')

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format:
			if message.file3 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.process_top_menu()
				elif message.function == '2':
					self.process_orders()
				elif message.function == '3':
					self.process_equipment()
				elif message.function == '4':
					self.process_settings()
			else:
				self.last_data = ''
			if message.file3 == '1':
				self.containerGUI.new_message(message)
			elif message.file3 == '2':
				self.dryerGUI.new_message(message)
			elif message.file3 == '3':
				self.extruderGUI.new_message(message)
			elif message.file3 == '4':
				self.locationGUI.new_message(message)
			elif message.file3 == '5':
				self.printerGUI.new_message(message)
			elif message.file3 == '6':
				self.spoolGUI.new_message(message)
			elif message.file3 == '7':
				self.colorGUI.new_message(message)
			elif message.file3 == '8':
				self.surfaceGUI.new_message(message)
			elif message.file3 == '9':
				self.settingsGUI.new_message(message)
			elif message.file3 == '10':
				self.printer_typeGUI.new_message(message)
			elif message.file3 == '11':
				self.client_order.new_message(message)
		if message.type == 'text' and message.file3 == '':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'Здравствуйте, Администратор ' + self.chat.user.name
		buttons = ['Заказы', 'Оборудование', 'Настройки']
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_orders(self):
		text = 'Все активные заказы'
		buttons = []
		for order in self.app.orders:
			buttons.append([f'{order.order_id}: {order.name}', order.order_id])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'], 2, 0)

	def show_equipment(self):
		buttons = self.texts.admin_equipment.copy()
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите оборудование', buttons, ['Назад'], 3, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		if self.message.btn_data == 'Заказы':
			self.show_orders()
		elif self.message.btn_data == 'Оборудование':
			self.show_equipment()
		elif self.message.btn_data == 'Настройки':
			self.settingsGUI.last_data = ''
			self.settingsGUI.first_message(self.message)

	def process_orders(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		else:
			self.message.instance_id = self.message.btn_data
			self.client_order.last_data = ''
			self.client_order.first_message(self.message)

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
			self.locationGUI.last_data = ''
			self.locationGUI.first_message(self.message)
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
			self.surfaceGUI.last_data = ''
			self.surfaceGUI.first_message(self.message)
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()