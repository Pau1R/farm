import sys
sys.path.append('../lib')
# from lib.Msg import Message
from lib.Gui import Gui
from lib.Texts import Texts
from lib.equipment.Equipment import Equipment
from lib.equipment.container.GUI import ContainerGUI
from lib.equipment.dryer.GUI import DryerGUI
from lib.equipment.extruder.GUI import ExtruderGUI
from lib.equipment.location.GUI import LocationGUI
from lib.equipment.printer_type.GUI import Printer_typeGUI
from lib.equipment.printer.GUI import PrinterGUI
from lib.equipment.spool.GUI import SpoolGUI
from lib.equipment.color.GUI import ColorGUI
from lib.equipment.surface.GUI import SurfaceGUI
from lib.settings.GUI import SettingsGUI
from lib.client.Order import Client_order
from lib.request.RequestGUI import RequestGUI

class Admin:
	address = ''

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

	requestGUI = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.texts = Texts(chat, address)

		self.containerGUI = ContainerGUI(app, chat, address + '/1')
		self.dryerGUI = DryerGUI(app, chat, address + '/2')
		self.extruderGUI = ExtruderGUI(app, chat, address + '/3')
		self.locationGUI = LocationGUI(app, chat, address + '/4')
		self.printer_typeGUI = Printer_typeGUI(app, chat, address + '/5')
		self.printerGUI = PrinterGUI(app, chat, address + '/6')
		self.spoolGUI = SpoolGUI(app, chat, address + '/7')
		self.colorGUI = ColorGUI(app, chat, address + '/8')
		self.surfaceGUI = SurfaceGUI(app, chat, address + '/9')
		self.settingsGUI = SettingsGUI(app, chat, address + '/10')
		
		self.client_order = Client_order(app, chat, address + '/11')
		self.requestGUI = RequestGUI(app, chat, address + '/12')

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
				self.printer_typeGUI.new_message(message)
			elif message.file3 == '6':
				self.printerGUI.new_message(message)
			elif message.file3 == '7':
				self.spoolGUI.new_message(message)
			elif message.file3 == '8':
				self.colorGUI.new_message(message)
			elif message.file3 == '9':
				self.surfaceGUI.new_message(message)
			elif message.file3 == '10':
				self.settingsGUI.new_message(message)
			elif message.file3 == '11':
				self.client_order.new_message(message)
			elif message.file3 == '12':
				self.requestGUI.new_message(message)
		if message.type == 'text' and message.file3 == '':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'Здравствуйте, Администратор ' + self.chat.user_name
		buttons = ['Заказы', 'Оборудование', 'Настройки']
		if len(self.app.requests):
			buttons.append(['Обращения в поддержку', 'request'])
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_orders(self):
		text = 'Все активные заказы'
		buttons = []
		for order in self.app.orders:
			buttons.append([f'{order.id}: {order.name}', order.id])
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
		elif self.message.btn_data == 'request':
			self.requestGUI.last_data = ''
			self.requestGUI.first_message(self.message)

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