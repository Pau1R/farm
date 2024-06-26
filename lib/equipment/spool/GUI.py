import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.Texts import Texts
from datetime import date
from datetime import timedelta

class SpoolGUI:
	address = ''

	app = None
	chat = None
	GUI = None
	spool = None
	texts = None

	last_data = ''

	quantity = 1
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
 
	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address)

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
					self.process_ordered()
				if function == '3':
					self.process_spool()
				if function == '4':
					self.process_change_weight()
				if function == '5':
					self.process_weight_input()
				if function == '6':
					self.process_add_new_spool()
				if function == '7':
					self.process_add_new_spool_type()
				if function == '8':
					self.process_add_new_spool_color()
				if function == '9':
					self.process_add_new_spool_weight()
				if function == '10':
					self.process_add_new_spool_price()
				if function == '11':
					self.process_add_new_spool_dried()
				if function == '12':
					self.process_add_new_spool_brand()
				if function == '13':
					self.process_add_delivery_date()
				if function == '14':
					self.process_add_confirmation()
				if function == '15':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.spools) > 0:
			text = 'Все катушки:'
		else:
			text = 'Катушки отсутствуют'
		buttons = []
		for spool in self.app.equipment.spools:
			if spool.status == 'stock':
				color_name = self.app.equipment.color_logic.get_color_name(spool.color_id)
				buttons.append([f'{spool.type} ({spool.id}) {color_name}', spool.id])
		buttons.sort(key=self.get_first_elem)
		buttons.extend(['Добавить', ['Катушки, ожидаемые к поставке', 'ordered'], 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_ordered(self):
		text = 'Заказанных катушек нет'
		for spool in self.app.equipment.spools:
			if spool.status == 'ordered':
				text = 'Катушки, ожидаемые к поставке:'
		buttons = []
		for spool in self.app.equipment.spools:
			if spool.status == 'ordered':
				color_name = self.app.equipment.color_logic.get_color_name(spool.color_id)
				buttons.append([f'{spool.type} ({spool.id}) {color_name} {self.app.functions.russian_date(spool.delivery_date_estimate)}', spool.id])
		buttons.sort(key=self.get_first_elem)
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 2, 0)

	def show_spool(self):
		text = f'Номер катушки: {self.spool.id}\n'
		text += f'Тип: {self.spool.type}\n'
		color_name = self.app.equipment.color_logic.get_color_name(self.spool.color_id)
		text += f'Цвет: {color_name}\n'
		text += f'Цена: {self.spool.price} рублей\n'
		text += f'Вес: {self.spool.weight} грамм\n'
		text += f'Использовано: {self.spool.used} грамм\n'
		if not self.spool.status == 'ordered':
			text += f'Сухая: {self.spool.dried}\n'
		text += f'Магазин/бренд: {self.spool.brand}\n'
		text += f'Дата добавления: {self.app.functions.russian_date(self.spool.date)}\n'
		if self.spool.status == 'ordered':
			date = self.app.functions.russian_date(self.spool.delivery_date_estimate)
			text += f'Дата поставки: {date}\n'
		text += f'Диаметр: {self.spool.diameter} mm\n'
		text += f'Плотность: {self.spool.density} г/см3\n'
		buttons = []
		if self.spool.status == 'ordered':
			buttons.append(['Катушка прибыла на склад', 'delivered'])
		buttons.extend(['Изменить вес', 'Удалить', 'Назад'])

		color_photo = self.app.equipment.color_logic.get_color_photo(self.spool.color_id)
		self.GUI.tell_photo_buttons(text, color_photo, buttons, buttons, 3, self.spool.id)

	def show_change_weight(self):
		text = 'Выберите действие'
		buttons = ['Добавить в метрах', 'Удалить в метрах', 'Добавить в граммах', 'Удалить в граммах']
		self.GUI.tell_buttons(text, buttons, buttons, 4, 0)

	def show_weight_input(self):
		self.chat.set_context(self.address, 5)
		text = 'Введите целочисленное кол-во'
		self.GUI.tell(text)

	def show_add_new_spool(self):
		buttons = ['1','2','3','4','5','6','7','8','9','10']
		self.GUI.tell_buttons('Выберите количество добавляемых катушек', buttons, [], 6, 0)

	def show_add_new_spool_type(self):
		self.GUI.tell_buttons('Выберите тип пластика', self.texts.spool_types.copy(), [], 7, 0)

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
		self.GUI.tell_buttons('Выберите цвет пластика', buttons, [], 8, 0)

	def show_add_new_spool_weight(self):
		self.GUI.tell_buttons('Выберите вес катушки', self.texts.spool_weight.copy(), [], 9, 0)

	def show_add_new_spool_price(self):
		self.chat.set_context(self.address, 10)
		self.GUI.tell('Введите цену за катушку в рублях')

	def show_add_new_spool_dried(self):
		if self.status == 'ordered':
			self.dried = 'Нет'
			self.show_add_new_spool_brand()
			return
		self.GUI.tell_buttons('Катушка высушена?', ['Да', 'Нет'], ['Да', 'Нет'], 11, 0)

	def show_add_new_spool_brand(self):
		self.chat.set_context(self.address, 12)
		self.GUI.tell('Введите название бренда/магазина')

	def show_add_delivery_date(self):
		buttons = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']
		self.GUI.tell_buttons('Через сколько дней ожидается поставка', buttons, [], 13, 0)

	def show_add_confirmation(self):
		text = 'Подтвердите добавление катушки'
		if self.quantity > 1:
			text = f'Подтвердите добавление {self.quantity} катушек'
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons(text, buttons, buttons, 14, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление катушки', buttons, buttons, 15, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.status = 'stock'
			self.show_add_new_spool()
		elif self.message.btn_data == 'ordered':
			self.show_ordered()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for spool in self.app.equipment.spools:
				if spool.id == int(self.message.btn_data):
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
		try:
			self.quantity = int(self.message.btn_data)
		except:
			self.show_add_new_spool()
		self.show_add_new_spool_type()

	def process_add_new_spool_type(self):
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
			spools = []
			for elem in range(1, self.quantity + 1):
				spool = self.app.equipment.create_new_spool(self.type, self.diameter, self.weight, self.density, self.color_id, self.dried, self.brand, self.used, self.price, self.status, self.delivery_date_estimate)
				spools.append(str(spool.id))
			if self.quantity == 1:
				self.spool = spool
				self.show_spool()
			else:
				spools = ','.join(spools)
				self.GUI.tell(f'Добавлены следующие номера катушек: {spools}')
				if self.status == 'ordered':
					self.show_ordered()
				else:
					self.show_top_menu()
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
		elif self.spool != None and self.spool.status == 'ordered':
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
				if spool.id == int(self.message.btn_data):
					self.spool = spool
					self.show_spool()

	def process_add_delivery_date(self):
		days = int(self.message.btn_data)
		self.delivery_date_estimate = date.today() + timedelta(days = days) # add days to current date
		self.show_add_confirmation()

#---------------------------- LOGIC ----------------------------

	def get_first_elem(self, element):
		return element[0]