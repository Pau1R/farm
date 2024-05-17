import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.Texts import Texts
from datetime import date

class SpoolGUI:
	address = '1/2/6'

	app = None
	chat = None
	GUI = None
	spool = None
	texts = None

	last_data = ''

	type = ''
	weight = 0
	color = ''
	dried = ''
	brand = ''
	used = 0

	change_weight_type = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
			if message.function == '2':
				self.process_spool()
			if message.function == '3':
				self.process_change_weight()
			if message.function == '4':
				self.process_weight_input()
			if message.function == '5':
				self.process_add_new_spool()
			if message.function == '6':
				self.process_add_new_spool_color()
			if message.function == '7':
				self.process_add_new_spool_weight()
			if message.function == '8':
				self.process_add_new_spool_price()
			if message.function == '9':
				self.process_add_new_spool_dried()
			if message.function == '10':
				self.process_add_new_spool_brand()
			if message.function == '11':
				self.process_add_confirmation()
			if message.function == '12':
				self.process_delete_confirmation()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.spools) > 0:
			text = 'Все катушки:'
		else:
			text = 'Катушки отсутствуют'
		buttons = []
		for spool in self.app.equipment.spools:
			buttons.append([f'{spool.id}: {spool.color} {spool.type}', spool.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_spool(self):
		text = f'Номер катушки: {self.spool.id}\nДата добавления: {self.spool.date}\n'
		text += f'Тип: {self.spool.type}\nДиаметр: {self.spool.diameter} mm\n'
		text += f'Вес: {self.spool.weight} грамм\nПлотность: {self.spool.density} г/см3\nЦвет: {self.spool.color}\n'
		text += f'Сухая: {self.spool.dried}\nМагазин/бренд: {self.spool.brand}\nИспользовано: {self.spool.used} грамм'
		buttons = ['Изменить вес', 'Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_change_weight(self):
		text = 'Выберите действие'
		buttons = ['Добавить в метрах', 'Удалить в метрах', 'Добавить в граммах', 'Удалить в граммах']
		self.GUI.tell_buttons(text, buttons, buttons, 3, 0)

	def show_weight_input(self):
		self.chat.set_context(self.address, 4)
		text = 'Введите целочисленное кол-во'
		self.GUI.tell(text)

	def show_add_new_spool(self):
		self.GUI.tell_buttons('Выберите тип пластика', self.texts.spool_types.copy(), [], 5, 0)

	def show_add_new_spool_color(self):
		self.GUI.tell_buttons('Выберите цвет пластика', self.texts.spool_colors.copy(), [], 6, 0)

	def show_add_new_spool_weight(self):
		self.GUI.tell_buttons('Выберите вес катушки', self.texts.spool_weight.copy(), [], 7, 0)

	def show_add_new_spool_price(self):
		self.chat.set_context(self.address, 8)
		self.GUI.tell('Введите цену за катушку в rub')

	def show_add_new_spool_dried(self):
		self.GUI.tell_buttons('Катушка высушена?', ['Да', 'Нет'], ['Да', 'Нет'], 9, 0)

	def show_add_new_spool_brand(self):
		self.chat.set_context(self.address, 10)
		self.GUI.tell('Введите название бренда/магазина')

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление катушки', buttons, buttons, 11, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление катушки', buttons, buttons, 12, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_spool()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for spool in self.app.equipment.spools:
				if self.message.btn_data == spool.id:
					self.spool = spool
					self.show_spool()

	def process_spool(self):
		if self.message.btn_data == 'Изменить вес':
			self.show_change_weight()
		elif self.message.btn_data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_change_weight(self):
		self.change_weight_type = self.message.btn_data
		self.show_weight_input()

	def process_weight_input(self):
		try:
			value = int(self.message.text)
		except:
			self.show_weight_input()
		dia = self.spool.diameter
		volume = (3.14159*(dia/10)*(dia/10)*100)/4
		if self.change_weight_type == 'Добавить в метрах':
			self.spool.weight += int(value * volume * self.spool.density)
		elif self.change_weight_type == 'Удалить в метрах':
			self.spool.weight -= int(value * volume * self.spool.density)
		elif self.change_weight_type == 'Добавить в граммах':
			self.spool.weight += value
		elif self.change_weight_type == 'Удалить в граммах':
			self.spool.weight -= value
		self.app.db.update_spool(self.spool)
		self.show_spool()

	def process_add_new_spool(self):
		self.type = self.message.btn_data
		self.show_add_new_spool_color()

	def process_add_new_spool_color(self):
		self.color = self.message.btn_data
		self.show_add_new_spool_weight()

	def process_add_new_spool_weight(self):
		self.weight = int(float(self.message.btn_data.split(" ")[0]) * 1000)
		self.show_add_new_spool_price()

	def process_add_new_spool_price(self):
		try:
			self.price = int(self.message.text)
			self.show_add_new_spool_dried()
		except:
			self.show_add_new_spool_price()

	def process_add_new_spool_dried(self):
		self.dried = self.message.btn_data
		self.show_add_new_spool_brand()

	def process_add_new_spool_brand(self):
		self.brand = self.message.text
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.diameter = self.texts.spool_diameter
			self.density = self.texts.spool_densities[self.texts.spool_types.index(self.type)]
			self.spool = self.app.equipment.create_new_spool(self.type, self.diameter, self.weight, self.density, self.color, self.dried, self.brand, self.used)
			text = f'Создана новая катушка:\nномер: {self.spool.id}\nтип: {self.spool.type}\nвес: {self.spool.weight} грамм\n'
			text += f'цвет: {self.spool.color}\nвысушена: {self.spool.dried}\nбренд/магазин: {self.spool.brand}'
			self.GUI.tell_permanent(text)
		self.type = ''
		self.color = ''
		self.dried = ''
		self.brand = ''
		self.price = 0
		self.diameter = 0.0
		self.weight = 0
		self.density = 0.0
		self.date = date.today()
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Катушка {self.spool.id} удалена')
			self.app.equipment.remove_spool(self.spool.id)
			self.spool = None
		self.show_top_menu()