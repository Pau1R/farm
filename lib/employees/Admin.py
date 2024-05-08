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
from lib.equipment.GUI.Printer import PrinterGUI
from lib.equipment.GUI.Spool import SpoolGUI
from lib.equipment.GUI.Surface import SurfaceGUI

class Admin:
	app = None
	chat = None
	equipmentGUI = None
	GUI = None
	message = None
	context = ''
	texts = Texts()

	containerGUI = None
	dryerGUI = None
	extruderGUI = None
	locationGUI = None
	printerGUI = None
	spoolGUI = None
	surfaceGUI = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat)

	def first_message(self, message):
		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.messages.append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_top_menu()
		elif context == 'top_menu':
			self.process_top_menu()
		elif context == 'orders':
			self.process_orders()
		elif context == 'equipment':
			self.process_equipment()

		elif self.equipmentGUI != None:
			self.equipmentGUI.new_message(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		text = 'Здравствуйте, Администратор ' + self.chat.user.name
		buttons = ['Заказы', 'Оборудование']
		self.GUI.tell_buttons(text, buttons, ['Заказы', 'Оборудование'])

	def show_orders(self):
		self.context = 'orders'
		buttons = []
		buttons.append('Назад')
		self.GUI.tell_buttons('Заказы:', buttons, ['Назад'])

	def show_equipment(self):
		self.context = 'equipment'
		buttons = self.texts.admin_equipment.copy()
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите оборудование', buttons, ['Назад'])

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Заказы':
			self.show_orders()
		elif self.message.data == 'Оборудование':
			self.show_equipment()

	def process_orders(self):
		self.context = ''
		if self.message.data == 'Назад':
			self.show_top_menu()

	def process_equipment(self):
		self.context = ''
		if self.message.data == 'Ящики':
			if self.containerGUI == None:
				self.containerGUI = ContainerGUI(self.app, self.chat)
				# self.containerGUI = ContainerGUI(self.bot, self.db, self.equipment, self.conf, self.chats, self.chat)
			self.equipmentGUI = self.containerGUI
		elif self.message.data == 'Сушилки':
			if self.dryerGUI == None:
				self.dryerGUI = DryerGUI(self.app, self.chat)
				# self.dryerGUI = DryerGUI(self.bot, self.db, self.equipment, self.conf, self.chats, self.chat)
			self.equipmentGUI = self.dryerGUI
		elif self.message.data == 'Экструдеры':
			if self.extruderGUI == None:
				self.extruderGUI = ExtruderGUI(self.app, self.chat)
				# self.extruderGUI = ExtruderGUI(self.bot, self.db, self.equipment, self.conf, self.chats, self.chat)
			self.equipmentGUI = self.extruderGUI
		elif self.message.data == 'Локации':
			if self.locationGUI == None:
				self.locationGUI = LocationGUI(self.app, self.chat)
				# self.locationGUI = LocationGUI(self.bot, self.db, self.equipment, self.conf, self.chats, self.chat)
			self.equipmentGUI = self.locationGUI
		elif self.message.data == 'Принтеры':
			if self.printerGUI == None:
				self.printerGUI = PrinterGUI(self.app, self.chat)
				# self.printerGUI = PrinterGUI(self.bot, self.db, self.equipment, self.conf, self.chats, self.chat)
			self.equipmentGUI = self.printerGUI
		elif self.message.data == 'Катушки':
			if self.spoolGUI == None:
				self.spoolGUI = SpoolGUI(self.app, self.chat)
				# self.spoolGUI = SpoolGUI(self.bot, self.db, self.equipment, self.conf, self.chats, self.chat)
			self.equipmentGUI = self.spoolGUI
		elif self.message.data == 'Поверхности':
			if self.surfaceGUI == None:
				self.surfaceGUI = SurfaceGUI(self.app, self.chat)
				# self.surfaceGUI = SurfaceGUI(self.bot, self.db, self.equipment, self.conf, self.chats, self.chat)
			self.equipmentGUI = self.surfaceGUI
		elif self.message.data == 'Назад':
			self.show_top_menu()
			self.equipmentGUI = None
		else:
			self.equipmentGUI = None

		if self.equipmentGUI != None:
			self.equipmentGUI.first_message(self.message)