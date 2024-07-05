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
		self.set_order()
		self.GUI.clear_order_chat(self.order.id)

		file = self.chat.next_level_id(self)
		function = message.function
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
		self.chat.add_if_text(self)

	def set_order(self):
		order_id = int(self.message.instance_id)
		for order in self.app.orders:
			if order.id == order_id:
				self.order = order
				return

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		buttons = []
		buttons.append(['Общие','general'])
		buttons.append(['Настройки печати','print_settings'])
		buttons.append(['Файлы, фото, ссылки','files'])
		buttons.append(['Финансы','finances'])
		buttons.append(['Доставка','delivery'])
		buttons.append(['Назад'])
		self.GUI.tell_buttons('Выберите тип параметров:', buttons, buttons, 1, self.order.id)

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
		buttons.append([f'Цвет: {color}','color'])
		designer = self.app.get_chat(order.assigned_designer_id)
		buttons.append([f'Назначенный дизайнер: {designer.user_name}','user_name'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Общие:', buttons, buttons, 2, order.id)
		
	def show_print_settings(self):
		order = self.order
		buttons = []
		buttons.append([f'Тип пластика: {order.plastic_type}','plastic_type'])
		buttons.append([f'Тип принтера: {order.printer_type}','printer_type'])
		buttons.append([f'Высота слоя: {order.layer_height}','layer_height'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Настройки печати:', buttons, buttons, 3, order.id)

	def show_files(self):
		order = self.order
		buttons = []
		buttons.append([f'stl файл: {1 if order.model_file else 0}','model_file'])
		buttons.append([f'Ссылка: {1 if order.link else 0}','link'])
		buttons.append([f'Чертежы/фото: {len(order.sketches)}','sketches'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Файлы:', buttons, buttons, 4, order.id)

	def show_finances(self):
		order = self.order
		buttons = []
		buttons.append([f'Цена: {int(order.price)} рублей','price'])
		buttons.append([f'Внесенная сумма: {int(order.payed)} рублей', 'payed'])
		buttons.append([f'Время удаления поддержек c 1 шт.: {int(order.support_time)}','support_time'])
		buttons.append([f'Процент предоплаты: {int(order.prepayment_percent)}','prepayment_percent'])
		buttons.append([f'Удаление поддержек: {order.support_remover}','support_remover'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Финансы:', buttons, buttons, 5, order.id)

	def show_delivery(self):
		order = self.order
		buttons = []
		buttons.append([f'Код оплаты: {order.pay_code}','pay_code'])
		buttons.append([f'Код получения/выдачи: {order.delivery_code}','delivery_code'])
		delivery = self.app.get_chat(order.delivery_user_id)
		buttons.append([f'Чат выдачи: {delivery}','delivery_user_id'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Доставка:', buttons, buttons, 6, order.id)

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
			self.chat.user.admin.last_data = ''
			self.chat.user.admin.show_orders()

	def process_general(self):
		data = self.message.btn_data
		if data == 'type':
			x = ''
		elif data == 'name':
			x = ''
		elif data == 'status':
			x = ''
		elif data == 'comment':
			x = ''
		elif data == 'priority':
			x = ''
		elif data == 'completion_date':
			x = ''
		elif data == 'quantity':
			x = ''
		elif data == 'color':
			x = ''
		elif data == 'user_name':
			x = ''
		elif data == 'Назад':
			self.show_top_menu()

	def process_print_settings(self):
		data = self.message.btn_data
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
		if data == '':
			x = ''
		elif data == 'model_file':
			x = ''
		elif data == 'link':
			x = ''
		elif data == 'sketches':
			x = ''
		elif data == 'Назад':
			self.show_top_menu()

	def process_finances(self):
		data = self.message.btn_data
		if data == 'price':
			x = ''
		elif data == 'payed':
			x = ''
		elif data == 'support_time':
			x = ''
		elif data == 'prepayment_percent':
			x = ''
		elif data == 'support_remover':
			x = ''
		elif data == 'Назад':
			self.show_top_menu()

	def process_delivery(self):
		data = self.message.btn_data
		if data == 'pay_code':
			x = ''
		elif data == 'delivery_code':
			x = ''
		elif data == 'delivery_user_id':
			x = ''
		elif data == 'Назад':
			self.show_top_menu()
