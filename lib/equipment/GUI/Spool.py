import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.Texts import Texts
from datetime import date

class SpoolGUI:
	app = None
	chat = None
	GUI = None
	spool = None
	texts = Texts()

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
		self.GUI = Gui(app, chat)

	def first_message(self, message):
		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.messages_append(message)
		# self.GUI.messages.append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_top_menu()
		elif context == 'top_menu':
			self.process_top_menu()

		elif context == 'spool':
			self.process_spool()
		elif context == 'change_weight':
			self.process_change_weight()
		elif context == 'weight_input':
			self.process_weight_input()

		elif context == 'add_new_spool':
			self.process_add_new_spool()
		elif context == 'add_new_spool_color':
			self.process_add_new_spool_color()
		elif context == 'add_new_spool_weight':
			self.process_add_new_spool_weight()
		elif context == 'add_new_spool_price':
			self.process_add_new_spool_price()
		elif context == 'add_new_spool_dried':
			self.process_add_new_spool_dried()
		elif context == 'add_new_spool_brand':
			self.process_add_new_spool_brand()
		elif context == 'add_confirmation':
			self.process_add_confirmation()
		elif context == 'delete_confirmation':
			self.process_delete_confirmation()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		if len(self.app.equipment.spools) > 0:
			text = 'Все катушки:'
		else:
			text = 'Катушки отсутствуют'
		buttons = []
		for spool in self.app.equipment.spools:
			buttons.append([f'{spool.id}: {spool.color} {spool.type}', spool.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'])

	def show_spool(self):
		self.context = 'spool'
		text = f'Номер катушки: {self.spool.id}\nДата добавления: {self.spool.date}\n'
		text += f'Тип: {self.spool.type}\nДиаметр: {self.spool.diameter} mm\n'
		text += f'Вес: {self.spool.weight} грамм\nПлотность: {self.spool.density} г/см3\nЦвет: {self.spool.color}\n'
		text += f'Сухая: {self.spool.dried}\nМагазин/бренд: {self.spool.brand}\nИспользовано: {self.spool.used} грамм'
		buttons = ['Изменить вес']
		buttons.extend(['Удалить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, buttons)

	def show_change_weight(self):
		self.context = 'change_weight'
		text = 'Выберите действие'
		buttons = ['Добавить в метрах', 'Удалить в метрах', 'Добавить в граммах', 'Удалить в граммах']
		self.GUI.tell_buttons(text, buttons, buttons)

	def show_weight_input(self):
		self.context = 'weight_input'
		text = 'Введите целочисленное кол-во'
		self.GUI.tell(text)

	def show_add_new_spool(self):
		self.context = 'add_new_spool'
		self.GUI.tell_buttons('Выберите тип пластика', self.texts.spool_types.copy(), [])

	def show_add_new_spool_color(self):
		self.context = 'add_new_spool_color'
		self.GUI.tell_buttons('Выберите цвет пластика', self.texts.spool_colors.copy(), [])

	def show_add_new_spool_weight(self):
		self.context = 'add_new_spool_weight'
		self.GUI.tell_buttons('Выберите вес катушки', self.texts.spool_weight.copy(), [])

	def show_add_new_spool_price(self):
		self.context = 'add_new_spool_price'
		self.GUI.tell('Введите цену за катушку в rub')

	def show_add_new_spool_dried(self):
		self.context = 'add_new_spool_dried'
		self.GUI.tell_buttons('Катушка высушена?', ['Да', 'Нет'], ['Да', 'Нет'])

	def show_add_new_spool_brand(self):
		self.context = 'add_new_spool_brand'
		self.GUI.tell('Введите название бренда/магазина')

	def show_add_confirmation(self):
		self.context = 'add_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить добавление')
		self.GUI.tell_buttons('Подтвердите добавление катушки', buttons, ['Подтверждаю', 'Отменить добавление'])

	def show_delete_confirmation(self):
		self.context = 'delete_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить удаление')
		self.GUI.tell_buttons('Подтвердите удаление катушки', buttons, ['Подтверждаю', 'Отменить удаление'])

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Добавить':
			self.show_add_new_spool()
		elif self.message.data == 'Назад':
			self.app.chat.user.employee.show_equipment()
		else:
			for spool in self.app.equipment.spools:
				if self.message.data == spool.id:
					self.spool = spool
					self.show_spool()

	def process_spool(self):
		self.context = ''
		if self.message.data == 'Изменить вес':
			self.show_change_weight()
		elif self.message.data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.data == 'Назад':
			self.show_top_menu()

	def process_change_weight(self):
		self.context = ''
		self.change_weight_type = self.message.data
		self.show_weight_input()

	def process_weight_input(self):
		self.context = ''
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
		self.context = ''
		self.type = self.message.data
		self.show_add_new_spool_color()

	def process_add_new_spool_color(self):
		self.context = ''
		self.color = self.message.data
		self.show_add_new_spool_weight()

	def process_add_new_spool_weight(self):
		self.context = ''
		self.weight = int(self.message.data.split(" ")[0]) * 1000
		self.show_add_new_spool_price()

	def process_add_new_spool_price(self):
		self.context = ''
		try:
			self.price = int(self.message.text)
			self.show_add_new_spool_dried()
		except:
			self.show_add_new_spool_price()

	def process_add_new_spool_dried(self):
		self.context = ''
		self.dried = self.message.data
		self.show_add_new_spool_brand()

	def process_add_new_spool_brand(self):
		self.context = ''
		self.brand = self.message.text
		self.show_add_confirmation()

	def process_add_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.diameter = self.texts.spool_diameter
			self.density = self.texts.spool_densitys[self.texts.spool_types.index(self.type)]
			self.spool = self.app.equipment.create_new_spool(self.type, self.diameter, self.weight, self.density, self.color, self.dried, self.brand, self.used)
			text = f'Создана новая катушка:\nномер: {self.spool.id}\nтип: {self.spool.type}\nвес: {self.spool.weight} грамм\n'
			text += f'цвет: {self.spool.color}\nвысушена: {self.spool.dried}\nбренд/магазин: {self.spool.brand}'
			self.GUI.tell(text)
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
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.GUI.tell(f'Катушка {self.spool.id} удалена')
			self.app.equipment.remove_spool(self.spool.id)
			self.spool = None
		self.show_top_menu()