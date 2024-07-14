import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from datetime import date, datetime, timedelta
from lib.client.Color import Client_color

class Edit:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.client_color = Client_color(app, chat, address + '/1')
		self.message = None
		self.order = None

	def first_message(self, message):
		self.message = message
		self.set_order()
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		function = message.function
		if not function in ['7','9','10']:
			self.set_order()
		self.GUI.clear_order_chat(self.order.id)

		file = self.chat.next_level_id(self)
		if message.data_special_format:
			if file == '1':
				self.client_color.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				elif function == '2':
					self.process_general()
				elif function == '3':
					self.process_print_settings()
				elif function == '4':
					self.process_files()
				elif function == '5':
					self.process_finances()
				elif function == '6':
					self.process_delivery()
				elif function == '7':
					self.process_value()
				elif function == '8':
					self.process_selection()
				elif function == '9':
					self.process_load_stl()
				elif function == '10':
					self.process_load_sketch()
		self.chat.add_if_text(self)

	def set_order(self):
		order_id = int(self.message.instance_id)
		for order in self.app.orders:
			if order.id == order_id:
				self.order = order
				return

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		order = self.order
		buttons = []
		buttons.append(['Общие','general'])
		buttons.append(['Настройки печати','print_settings'])
		buttons.append(['Файлы, ссылка, фото','files'])
		buttons.append(['Финансы','finances'])
		buttons.append(['Доставка','delivery'])
		buttons.append(['Назад'])
		self.GUI.tell_buttons(f'Выберите тип параметров заказа {order.id}:', buttons, buttons, 1, order.id)

	def show_general(self):
		order = self.order
		data = self.app.data

		buttons = []
		buttons.append([f'Название: {order.name}','name'])
		buttons.append([f'Тип заказа: {data.types[order.type]}','type'])
		status = order.logical_status
		if not status:
			status = order.physical_status
		buttons.append([f'Статуc: {data.statuses[status]}','status'])
		buttons.append([f'Комментарий: {order.comment}','comment'])
		buttons.append([f'Приоритет: {order.priority}','priority'])
		if order.type == 'sketch':
			confirmed = 'нет'
			if order.confirmed:
				confirmed = 'да'
			buttons.append([f'Подтвержден клиентом: {confirmed}','confirmed'])
		date = self.app.functions.russian_date(order.completion_date)
		buttons.append([f'Дата готовности: {date}','completion_date'])
		buttons.append([f'Количество экземпляров: {order.quantity}','quantity'])
		buttons.append([f'Качество: {data.quality[order.quality]}','quality'])
		buttons.append([f'Вес экземпляра: {int(order.weight)}','weight'])
		color = self.app.equipment.color_logic.get_color_name(order.color_id)
		buttons.append([f'Цвет: {color}','color_id'])
		designer = ''
		if order.designer_id:
			designer = self.app.get_chat(order.designer_id).user_name
		buttons.append([f'Назначенный дизайнер: {designer}','designer_id'])
		buttons.append([f'Информация: {order.miscellaneous}','miscellaneous'])
		buttons.append('Назад')
		self.GUI.tell_buttons(f'Редактирование общих параметров заказа {order.id}:', buttons, buttons, 2, order.id)
		
	def show_print_settings(self):
		order = self.order
		buttons = []
		buttons.append([f'Тип пластика: {order.plastic_type}','plastic_type'])
		if order.printer_type:
			printer_type = self.app.printer_type_logic.get_printer_type(order.printer_type)
			printer_type = printer_type.name
		else:
			printer_type = ''
		buttons.append([f'Тип принтера: {printer_type}','printer_type'])
		buttons.append([f'Высота слоя: {order.layer_height}','layer_height'])
		buttons.append('Назад')
		self.GUI.tell_buttons(f'Редактирование настроек печати заказа {order.id}:', buttons, buttons, 3, order.id)

	def show_files(self):
		order = self.order
		buttons = []
		buttons.append([f'stl файл: {1 if order.model_file else 0}','model_file'])
		buttons.append([f'Ссылка: {1 if order.link else 0}','link'])
		buttons.append([f'Чертежы/фото: {len(order.sketches)}','sketches'])
		buttons.append('Назад')
		self.GUI.tell_buttons(f'Редактирование файлов заказа {order.id}:', buttons, buttons, 4, order.id)

	def show_finances(self):
		order = self.order
		buttons = []
		buttons.append([f'Цена: {int(order.price)} рублей','price'])
		buttons.append([f'Внесенная сумма: {int(order.payed)} рублей', 'payed'])
		buttons.append([f'Время удаления поддержек c 1 шт.: {int(order.support_time)}','support_time'])
		buttons.append([f'Процент предоплаты: {int(order.prepayment_percent)}','prepayment_percent'])
		remover = order.support_remover
		if not remover:
			remover = 'Студия'
		buttons.append([f'Удаление поддержек: {remover}','support_remover'])
		buttons.append('Назад')
		self.GUI.tell_buttons(f'Редактирование параметров оплаты заказа {order.id}:', buttons, buttons, 5, order.id)

	def show_delivery(self):
		order = self.order
		buttons = []
		buttons.append([f'Код оплаты: {order.pay_code}','pay_code'])
		buttons.append([f'Код получения/выдачи: {order.delivery_code}','delivery_code'])
		if order.delivery_user_id:
			delivery = self.app.get_chat(order.delivery_user_id)
			delivery = delivery.user_name
		else:
			delivery = ''
		buttons.append([f'Точка выдачи: {delivery}','delivery_user_id'])
		buttons.append('Назад')
		self.GUI.tell_buttons(f'Редактирование параметров получения/выдачи заказа {order.id}:', buttons, buttons, 6, order.id)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'general':
			self.show_general()
		elif data == 'print_settings':
			self.show_print_settings()
		elif data == 'files':
			self.show_files()
		elif data == 'finances':
			self.show_finances()
		elif data == 'delivery':
			self.show_delivery()
		elif data == 'Назад':
			self.chat.user.admin.order_GUI.last_data = ''
			self.chat.user.admin.order_GUI.order = self.order
			self.chat.user.admin.order_GUI.show_order()
			return
		self.parameters_type = data

	def process_general(self):
		data = self.message.btn_data
		order = self.order
		self.desired_field = data
		dictionary = self.app.data
		buttons = []
		if data == 'name':
			self.input_value(data, order.name)
		elif data == 'type':
			current_value = dictionary.types[order.type]
			buttons = [[value, f'{data}^{key}'] for key, value in dictionary.types.items()]
			self.input_selection(data, current_value, buttons)
		elif data == 'status':
			current_value = order.logical_status
			if not current_value:
				current_value = order.physical_status
			current_value = dictionary.statuses[current_value] # translate to russian
			buttons = [[value, f'{data}^{key}'] for key, value in dictionary.statuses.items()]
			self.input_selection(data, current_value, buttons)
		elif data == 'comment':
			self.input_value(data, order.comment)
		elif data == 'priority':
			self.input_value(data, order.priority)
		elif data == 'confirmed':
			current_value = 'нет'
			if order.confirmed:
				current_value = 'да'
			buttons = [['Да','confirmed^1'], ['Нет','confirmed^0']]
			self.input_selection(data, current_value, buttons)
		elif data == 'completion_date':
			today = date.today()
			completion_date = order.completion_date
			current = self.app.functions.russian_date(completion_date)
			def generate_buttons(start_date, num_days):
				return [
					[self.app.functions.russian_date(start_date + timedelta(days=i)),
					 f'completion_date^{(start_date + timedelta(days=i)).strftime("%Y-%m-%d")}']
					for i in range(num_days)
				]
			if completion_date and completion_date >= today:
				days_until_completion = (completion_date - today).days
				if days_until_completion <= 3:
					buttons = generate_buttons(today, 10)
				else:
					start_date = completion_date - timedelta(days=4)
					buttons = generate_buttons(start_date, 10)
			else:
				buttons = generate_buttons(today, 10)
			self.input_selection(data, current, buttons)
		elif data == 'quantity':
			self.input_value(data, order.quantity)
		elif data == 'quality':
			current = dictionary.quality[order.quality]
			buttons = [[value, f'{data}^{key}'] for key, value in dictionary.quality.items()]
			self.input_selection(data, current, buttons)
		elif data == 'weight':
			self.input_value(data, int(order.weight))
		elif data == 'color_id':
			self.client_color.last_data = ''
			self.client_color.first_message(self.message)
		elif data == 'designer_id':
			designer = self.app.get_chat(order.designer_id)
			designers = self.app.get_chats('Дизайнер')
			for row in designers:
				buttons.append([row.user_name, f'{data}^{row.user_id}'])
			self.input_selection(data, designer.user_name, buttons)
		elif data == 'miscellaneous':
			self.input_value(data, order.miscellaneous)
		elif data == 'Назад':
			self.show_top_menu()

	def process_print_settings(self):
		data = self.message.btn_data
		order = self.order
		self.desired_field = data
		if data == 'plastic_type':
			buttons = self.app.equipment.spool_logic.get_all_types()
			buttons = [[button, f'{data}^{button}'] for button in buttons]
			buttons.append(['любой базовый', '{data}^basic'])
			self.input_selection(data, order.plastic_type, buttons)
		elif data == 'printer_type':
			printer_type = self.app.printer_type_logic.get_printer_type(order.printer_type)
			buttons = self.app.printer_type_logic.get_all_types()
			buttons = [[button[0], f'{data}^{button[1]}'] for button in buttons]
			buttons.append(['Любой',f'{data}^*'])
			self.input_selection(data, printer_type.name, buttons)
		elif data == 'layer_height':
			self.input_value(data, order.layer_height)
		elif data == 'Назад':
			self.show_top_menu()

	def process_files(self):
		data = self.message.btn_data
		order = self.order
		self.desired_field = data
		if data == 'model_file':
			self.show_load_stl()
		elif data == 'link':
			self.input_value(data, order.link)
		elif data == 'sketches':
			self.show_load_sketch()
		elif data == 'Назад':
			self.show_top_menu()

	def process_finances(self):
		data = self.message.btn_data
		order = self.order
		self.desired_field = data
		if data == 'price':
			self.input_value(data, int(order.price))
		elif data == 'payed':
			self.input_value(data, int(order.payed))
		elif data == 'support_time':
			self.input_value(data, int(order.support_time))
		elif data == 'prepayment_percent':
			self.input_value(data, int(order.prepayment_percent))
		elif data == 'support_remover':
			buttons = [['Клиент',f'{data}^Клиент']]
			buttons.append(['Студия',f'{data}^'])
			remover = order.support_remover
			if not remover:
				remover = 'Студия'
			self.input_selection(data, remover, buttons)
		elif data == 'Назад':
			self.show_top_menu()

	def process_delivery(self):
		data = self.message.btn_data
		order = self.order
		self.desired_field = data
		if data == 'pay_code':
			self.input_value(data, order.pay_code)
		elif data == 'delivery_code':
			self.input_value(data, order.delivery_code)
		elif data == 'delivery_user_id':
			delivery = self.app.get_chat(order.delivery_user_id)
			deliverys = self.app.get_chats('Дизайнер')
			buttons = []
			for row in deliverys:
				buttons.append([row.user_name, f'delivery_user_id^{row.user_id}'])
			self.input_selection(data, delivery.user_name, buttons)
		elif data == 'Назад':
			self.show_top_menu()

#---------------------------- INPUT SHOW ----------------------------

	def input_value(self, field_name, current_value):
		self.chat.set_context(self.address, 7)
		if not field_name and not current_value:
			field_name = self.field_name
			current_value = self.current_value
		else:
			self.field_name = field_name
			self.current_value = current_value
		field_name = self.app.data.attributes[field_name] # translating to russian
		text = f'Текущее значение поля "{field_name}" заказа {self.order.id}: "{current_value}"\n\nВведите новое значение'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 7, self.order.id)

	def input_selection(self, field_name, current_value, buttons):
		order = self.order
		field_name = self.app.data.attributes[field_name] # translating to russian
		text = f'Текущее значение поля "{field_name}" заказа {order.id}: "{current_value}"\n\nВыберите новое значение'
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'], 8, order.id)

	def value_error(self):
		self.GUI.tell('Ошибка ввода данных')

#---------------------------- INPUT PROCESS ----------------------------

	def process_value(self):
		text = self.message.text
		data = self.desired_field
		if self.message.btn_data == 'Назад':
			self.chat.context = ''
			self.message.btn_data = self.parameters_type
			self.process_top_menu()
			return
		if data in ['name', 'comment', 'link', 'miscellaneous']: # str
			new = text
		elif data in ['priority','quantity','weight','price','payed','support_time','prepayment_percent','pay_code','delivery_code','completion_date']: # int
			try:
				new = int(text)
			except:
				self.value_error()
				self.input_value('','')
				return
		elif data in ['layer_height']:
			try:
				new = float(text)
			except:
				self.value_error()
				self.input_value('','')
				return
		setattr(self.order, data, new)
		self.app.db.update_order(self.order)
		self.message.btn_data = self.parameters_type
		self.process_top_menu()

	def process_selection(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.message.btn_data = self.parameters_type
			self.process_top_menu()
			return
		else:
			data, value = data.split('^')
		if data == 'status':
			self.set_status(value)
			return
		elif data not in ['type','confirmed','completion_date','quality','designer_id','plastic_type','printer_type','support_remover','delivery_user_id']: # selection
			return
		if data in ['completion_date']:
			value = datetime.strptime(value, "%Y-%m-%d").date()
		if data in ['designer_id','delivery_user_id']:
			value = int(value)
		setattr(self.order, data, value)
		self.app.db.update_order(self.order)
		self.message.btn_data = self.parameters_type
		self.process_top_menu()

#---------------------------- model_file ----------------------------

	def show_load_stl(self):
		self.chat.set_context(self.address, 9)
		text = 'Загрузите 3д файл. Поддерживаются следующие форматы: ' + ', '.join(self.app.data.supported_files)
		buttons = ['Назад']
		if self.order.model_file:
			self.GUI.tell_document(self.order.model_file, '')
		self.GUI.tell_buttons(text, buttons, buttons, 9, self.order.id)

	def show_extention_error(self):
		self.GUI.tell('Неверный формат файла')
		self.show_load_stl()

	def process_load_stl(self):
		self.chat.context = ''
		if self.message.btn_data == 'Назад':
			self.show_files()
		elif self.message.type == 'document' and self.message.file_name.split(".")[-1] == 'stl':
			self.order.model_file = self.message.file_id
			self.app.db.update_order(self.order)
			self.show_files()
		else:
			self.show_extention_error()

#---------------------------- sketches ----------------------------

	def show_load_sketch(self):
		self.chat.set_context(self.address, 10)
		text = 'Загрузите файл с чертежами либо фото предмета'
		for x, file in enumerate(self.order.sketches):
			buttons = [['Удалить', f'delete^{x}']]
			if file[1] == 'photo':
				self.GUI.tell_photo_buttons('', file[0], buttons, buttons, 10, self.order.id)
			else:
				self.GUI.tell_document_buttons(file[0], '', buttons, buttons, 10, self.order.id)
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 10, self.order.id)

	def process_load_sketch(self):
		self.chat.context = ''
		data = self.message.btn_data
		if data.startswith('delete'):
			value = int(data.split('^')[1])
			self.order.sketches.pop(value)
			self.app.db.update_order(self.order)
		elif data != 'Назад':
			file_id = self.message.file_id
			type_ = self.message.type
			self.order.sketches.append([file_id, type_])
			self.app.db.update_order(self.order)
		self.show_files()

#---------------------------- LOGIC ----------------------------

	def set_status(self, value):
		order = self.order
		if value in self.app.data.logical_statuses:
			order.logical_status = value
			order.physical_status = 'prepare'
		elif value in self.app.data.physical_statuses:
			order.logical_status = ''
			order.physical_status = value
		self.app.db.update_order(order)
		self.message.btn_data = self.parameters_type
		self.process_top_menu()