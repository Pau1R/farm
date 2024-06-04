class Texts:
	chat = None
	address = ''

	def __init__(self, chat, address):
		self.chat = chat

#---------------------------- OWNER TEXTS ----------------------------

	owner_employee_menu = """
Сотрудники

(Для добавления сотрудника ему нужно отправить в бот сообщение: я_хочу_стать_сотрудником.
После этого нужно принять запрос и назначить ему необходимые роли.)"""

#---------------------------- ADMIN TEXTS ----------------------------

	admin_equipment = ['Локации', 'Типы принтеров', 'Принтеры', 'Экструдеры', 'Поверхности', 'Сушилки', 'Катушки', 'Цвета', 'Ящики']

	spool_diameter = 1.75
	spool_types = ['PLA', 'PETG', 'ABS', 'PC', 'TPE']
	spool_densities = [1.24, 1.27, 1.04, 1.2, 1.2]

	spool_weight = ['0.1 кг', '0.5 кг', '0.7 кг', '0.9 кг', '1 кг', '2 кг', '2.5 кг', '3 кг']

	spool_colors = ['белый', 'черный', 'темно-серый', 'серый', 'светло-серый']
	spool_colors.extend(['красный', 'оранжевый', 'жёлтый', 'зелёный', 'голубой', 'синий', 'фиолетовый'])

	surface_types = ['PEI', 'Стекло']

#---------------------------- DESIGNER TEXTS ----------------------------

	def designer_orders_design_text(self, order_timer, orders):
		text = f'Текущая модель в работе: {order_timer}\n\nВыберите Модель'
		if orders == []:
			text = 'Модели отсутствуют'
		return text

	def designer_orders_design_btns(self, orders):
		buttons = []
		for order in orders:
			buttons.append([order.id + ': ' + order.name, order.id])
		buttons.extend(['Назад'])
		return buttons

	def designer_order_text(self, order):
		return f'номер: {order.id}\nназвание: {order.name}'

	def designer_order_btns(self, order_timer, order):
		buttons = [['Описание', 'info'], ['Уточнить у клиента', 'clarify'], ['Моделирование успешно окончено', 'finish'], ['Добавить скриншоты готовой модели','screenshots']]
		if order_timer == '':
			buttons.extend(['Начать учет времени', 'start_timer'])
		elif order_timer == order.id:
			buttons.extend(['Окончить учет времени', 'stop_timer'])
		buttons.extend(['Назад'])
		return buttons

	def designer_orders_validate_text(self, order_timer, orders):
		text = f'Выберите модель для валидации'
		if orders == []:
			text = 'Модели отсутствуют'
		return text

	def designer_orders_validate_btns(self, orders, chat):
		buttons = []
		orders = orders.copy()
		orders.sort(key=self.get_object_date)
		for order in orders:
			if order.status == 'validate' and (order.assinged_designer_id == str(chat.user_id) or order.assinged_designer_id == 0):
				buttons.append([str(order.id) + ': ' + order.name, order.id])
		buttons.extend(['Назад'])
		return buttons

	def designer_order_validate_text(self, order):
		text = f'Заказ № {order.id} "{order.name}" \nДата добавления: {order.date}'
		if order.quantity > 1:
			text += f'\nКоличество экземпляров: {order.quantity}'
		if not (order.conditions == '' or order.conditions == None):
			text += f'\nУсловия эксплуатации: {order.conditions}' 
		if not (order.comment == '' or order.comment == None):
			text += f'\nКомментарий клиента: {order.comment}'
		return text

	order_validate_accept_time_btns = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']

	order_validate_accept_time_minutes_btns = ['5','10','15','20','25','30','35','40','45','50','55']

	def get_object_date(self, object):
		return object.date