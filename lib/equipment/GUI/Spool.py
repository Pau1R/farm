import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.Texts import Texts
from datetime import date
from datetime import timedelta

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
	color_id = ''
	dried = ''
	brand = ''
	used = 0
	price = 0
	status = ''
	delivery_date_estimate = None

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
			if message.function == '13':
				self.process_ordered()
			if message.function == '14':
				self.process_add_delivery_date()
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
			if spool.status == 'stock':
				buttons.append([f'{spool.type} ({spool.id}) {spool.color_name()}', spool.id])
		buttons.sort(key=self.get_first_elem)
		buttons.extend(['Добавить', ['Катушки, ожидаемые к поставке', 'ordered'], 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_spool(self):
		text = f'Номер катушки: {self.spool.id}\n'
		text += f'Тип: {self.spool.type}\n'
		text += f'Цвет: {self.spool.color_name()}\n'
		text += f'Цена: {self.spool.price} рублей\n'
		text += f'Вес: {self.spool.weight} грамм\n'
		text += f'Использовано: {self.spool.used} грамм\n'
		if not self.spool.status == 'ordered':
			text += f'Сухая: {self.spool.dried}\n'
		text += f'Магазин/бренд: {self.spool.brand}\n'
		text += f'Дата добавления: {self.spool.date}\n'
		if self.spool.status == 'ordered':
			text += f'Дата поставки: {self.spool.delivery_date_estimate}\n'
		text += f'Диаметр: {self.spool.diameter} mm\n'
		text += f'Плотность: {self.spool.density} г/см3\n'
		buttons = []
		if self.spool.status == 'ordered':
			buttons.append(['Катушка прибыла на склад', 'delivered']) # TODO: process delivered spool
		buttons.extend(['Изменить вес', 'Удалить', 'Назад'])

		self.GUI.tell_photo_buttons(text, self.spool.color_photo(), buttons, buttons, 2, self.spool.id)

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
		buttons = []
		for color in self.app.equipment.colors:
			if color.parent_id == 0:
				buttons.append([color.name, color.id])
			else:
				for col in self.app.equipment.colors:
					if col.id == color.parent_id:
						buttons.append([col.name + '-' + color.name.lower(), color.id])
		buttons.sort(key=self.get_first_elem)
		self.GUI.tell_buttons('Выберите цвет пластика', buttons, [], 6, 0)

	def show_add_new_spool_weight(self):
		self.GUI.tell_buttons('Выберите вес катушки', self.texts.spool_weight.copy(), [], 7, 0)

	def show_add_new_spool_price(self):
		self.chat.set_context(self.address, 8)
		self.GUI.tell('Введите цену за катушку в рублях')

	def show_add_new_spool_dried(self):
		if self.status == 'ordered':
			self.dried = 'Нет'
			self.show_add_new_spool_brand()
			return
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

	def show_ordered(self):
		text = 'Заказанных катушек нет'
		for spool in self.app.equipment.spools:
			if spool.status == 'ordered':
				text = 'Катушки, ожидаемые к поставке:'
		buttons = []
		for spool in self.app.equipment.spools:
			if spool.status == 'ordered':
				buttons.append([f'{spool.type} ({spool.id}) {spool.color_name()} {spool.delivery_date_estimate}', spool.id])
		buttons.sort(key=self.get_first_elem)
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 13, 0)

	def show_add_delivery_date(self):
		buttons = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']
		self.GUI.tell_buttons('Через сколько дней ожидается поставка', buttons, [], 14, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.status = 'stock'
			self.show_add_new_spool() # TODO: add spools amount query
		elif self.message.btn_data == 'ordered':
			self.show_ordered()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for spool in self.app.equipment.spools:
				if spool.id == self.message.btn_data :
					self.spool = spool
					self.show_spool()

	def process_spool(self):
		data = self.message.btn_data
		if data == 'delivered':
			self.spool.status = 'stock'
			self.app.db.update_spool(self.spool)
			self.show_ordered()
		elif data == 'Изменить вес':
			self.show_change_weight()
		elif data == 'Удалить':
			self.show_delete_confirmation()
		elif data == 'Назад':
			if self.spool.status == 'ordered':
				self.show_ordered()
			else:
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
		self.color_id = int(self.message.btn_data)
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
		if self.status == 'ordered':
			self.show_add_delivery_date()
		else:
			self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.diameter = self.texts.spool_diameter
			self.density = self.texts.spool_densities[self.texts.spool_types.index(self.type)]
			self.spool = self.app.equipment.create_new_spool(self.type, self.diameter, self.weight, self.density, self.color_id, self.dried, self.brand, self.used, self.price, self.status, self.delivery_date_estimate)
			self.show_spool()
			# text = f'Создана новая катушка:\n'
			# text += f'Номер: {self.spool.id}\n'
			# text += f'Тип: {self.spool.type}\n'
			# text += f'Цвет: {self.spool.color_name()}\n'
			# text += f'Цена: {self.spool.price} рублей\n'
			# text += f'Вес: {self.spool.weight} грамм\n'
			# text += f'Высушена: {self.spool.dried}\n'
			# text += f'Бренд/магазин: {self.spool.brand}'
			# self.GUI.tell_permanent(text)
		self.type = ''
		self.color_id = 0
		self.dried = ''
		self.brand = ''
		self.price = 0
		self.diameter = 0.0
		self.weight = 0
		self.density = 0.0
		self.date = date.today()
		self.delivery_date_estimate = None
		# if self.status == 'ordered':
		# 	self.show_ordered()
		# else:
		# 	self.show_top_menu()
		self.status = ''

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Катушка {self.spool.id} удалена')
			self.app.equipment.remove_spool(self.spool.id)
			if self.spool.status == 'ordered':
				self.show_ordered()
			else:
				self.show_top_menu()
			self.spool = None
		if self.spool != None and self.spool.status == 'ordered':
			self.show_ordered()
		else:
			self.show_top_menu()

	def process_ordered(self):
		if self.message.btn_data == 'Добавить':
			self.status = 'ordered'
			self.show_add_new_spool()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()
		else:
			for spool in self.app.equipment.spools:
				if spool.id == self.message.btn_data:
					self.spool = spool
					self.show_spool()

	def process_add_delivery_date(self):
		days = int(self.message.btn_data)
		self.delivery_date_estimate = date.today() + timedelta(days = days) # add days to current date
		self.show_add_confirmation()

#---------------------------- LOGIC ----------------------------

	def get_first_elem(self, element):
		return element[0]