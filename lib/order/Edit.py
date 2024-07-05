import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Edit:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
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
		if function != '7':
			self.set_order()
		self.GUI.clear_order_chat(self.order.id)

		file = self.chat.next_level_id(self)
		if message.data_special_format:
			if file == '1':
				return
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
		buttons.append(['Файлы, фото, ссылки','files'])
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
		date = self.app.functions.russian_date(order.completion_date)
		buttons.append([f'Дата готовности: {date}','completion_date'])
		buttons.append([f'Количество экземпляров: {order.quantity}','quantity'])
		color = self.app.equipment.color_logic.get_color_name(order.color_id)
		buttons.append([f'Цвет: {color}','color_id'])
		designer = self.app.get_chat(order.assigned_designer_id)
		buttons.append([f'Назначенный дизайнер: {designer.user_name}','assigned_designer_id'])
		buttons.append('Назад')
		self.GUI.tell_buttons(f'Редактирование общих параметров заказа {order.id}:', buttons, buttons, 2, order.id)
		
	def show_print_settings(self):
		order = self.order
		buttons = []
		buttons.append([f'Тип пластика: {order.plastic_type}','plastic_type'])
		buttons.append([f'Тип принтера: {order.printer_type}','printer_type'])
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
		buttons.append([f'Удаление поддержек: {order.support_remover}','support_remover'])
		buttons.append('Назад')
		self.GUI.tell_buttons(f'Редактирование параметров оплаты заказа {order.id}:', buttons, buttons, 5, order.id)

	def show_delivery(self):
		order = self.order
		buttons = []
		buttons.append([f'Код оплаты: {order.pay_code}','pay_code'])
		buttons.append([f'Код получения/выдачи: {order.delivery_code}','delivery_code'])
		delivery = self.app.get_chat(order.delivery_user_id)
		buttons.append([f'Чат выдачи: {delivery}','delivery_user_id'])
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
		elif data == 'completion_date':
			x = ''
		elif data == 'quantity':
			self.input_value(data, order.quantity)
		elif data == 'color_id': # TODO: rerun color selection
			x = ''
		elif data == 'assigned_designer_id':
			x = ''
		elif data == 'Назад':
			self.show_top_menu()

	def process_print_settings(self):
		data = self.message.btn_data
		order = self.order
		self.desired_field = data
		if data == 'plastic_type':
			x = ''
		elif data == 'printer_type':
			x = ''
		elif data == 'layer_height':
			x = ''
		elif data == 'Назад':
			self.show_top_menu()

	def process_files(self):
		data = self.message.btn_data
		order = self.order
		self.desired_field = data
		if data == '':
			x = ''
		elif data == 'model_file': # TODO: think
			x = ''
		elif data == 'link':
			self.input_value(data, order.link)
		elif data == 'sketches': # TODO: think
			x = ''
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
			x = ''
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
			x = ''
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
		# self.GUI.tell(text)
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 7, self.order.id)

	def input_selection(self, field_name, current_value, buttons):
		order = self.order
		text = f'Текущее значение поля "{field_name}" заказа {order.id}: "{current_value}"\n\nВыберите новое значение'
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 8, order.id)

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
		if data in ['name', 'comment', 'link']: # str
			new = text
		elif data in ['priority','quantity','price','payed','support_time','prepayment_percent','pay_code','delivery_code','completion_date']: # int
			try:
				new = int(text)
			except:
				self.value_error()
				self.input_value('','')
				return
		elif data in ['layer_height']: # float
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
		if data in ['type','assigned_designer_id','plastic_type','printer_type','support_remover','delivery_user_id']: # selection
			x = ''
		elif data == 'status':
			self.set_status(value)
			return
		
		setattr(self.order, data, value)
		self.app.db.update_order(self.order)
		self.message.btn_data = self.parameters_type
		self.process_top_menu()

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