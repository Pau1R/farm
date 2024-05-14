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

#---------------------------- DELIVERY TEXTS ----------------------------

	def delivery_top_menu(self, name):
		return f'Здравствуйте, {name}. Для выдачи заказа нажмите на кнопку'

	def delivery_issue_order(self, order):
		return f'Заказ {order} оплачен, можно выдавать'

	def delivery_pay_for_order(self, order, price):
		return f'Заказ {order} не оплачен, необходимо принять наличными: {price} рублей'  # get order price

#---------------------------- ADMIN TEXTS ----------------------------

	admin_equipment = ['Локации', 'Принтеры', 'Экструдеры', 'Поверхности', 'Сушилки', 'Катушки', 'Цвета', 'Ящики']

	spool_diameter = 1.75
	spool_types = ['PLA', 'PETG', 'ABS', 'PC', 'TPE']
	spool_densities = [1.24, 1.27, 1.04, 1.2, 1.2]

	spool_weight = ['0.1 кг', '0.5 кг', '0.7 кг', '0.9 кг', '1 кг', '2 кг', '2.5 кг', '3 кг']

	spool_colors = ['белый', 'черный', 'темно-серый', 'серый', 'светло-серый']
	spool_colors.extend(['красный', 'оранжевый', 'жёлтый', 'зелёный', 'голубой', 'синий', 'фиолетовый'])

	surface_types = ['PEI', 'Стекло']

#---------------------------- DESIGNER TEXTS ----------------------------

	def designer_top_menu_text(self, name, models):
		text = f'Здравствуйте, дизайнер {name}.\n\n'
		if models > 0:
			text += f'У вас {models} задач в очереди'
		else:
			text += 'Задачи отсутствуют'
		return text

	designer_top_menu_btns = [['Разработка моделей по чертежу', 'design'], ['Валидация моделей', 'validate'], ['Настройка параметрических моделей','parametric']]

	def designer_orders_design_text(self, order_timer, orders):
		text = f'Текущая модель в работе: {order_timer}\n\nВыберите Модель'
		if orders == []:
			text = 'Модели отсутствуют'
		return text

	def designer_orders_design_btns(self, orders):
		buttons = []
		for order in orders:
			buttons.append([order.order_id + ': ' + order.name, order.order_id])
		buttons.extend(['Назад'])
		return buttons

	def designer_order_text(self, order):
		return f'номер: {order.order_id}\nназвание: {order.name}'

	def designer_order_btns(self, order_timer, order):
		buttons = [['Описание', 'info'], ['Уточнить у клиента', 'clarify'], ['Моделирование успешно окончено', 'finish'], ['Добавить скриншоты готовой модели','screenshots']]
		if order_timer == '':
			buttons.extend(['Начать учет времени', 'start_timer'])
		elif order_timer == order.order_id:
			buttons.extend(['Окончить учет времени', 'stop_timer'])
		buttons.extend(['Назад'])
		return buttons

	def designer_orders_validate_text(self, order_timer, orders):
		text = f'Валидация моделей.\n\nТекущая модель в работе: {order_timer}\n\nВыберите модель'
		if orders == []:
			text = 'Модели отсутствуют'
		return text

	def designer_orders_validate_btns(self, orders, chat):
		buttons = []
		for order in orders:
			if order.status == 'validate' and (order.assinged_designer_id == chat.user_id or order.assinged_designer_id == ''):
				buttons.append([str(order.order_id) + ': ' + order.name, order.order_id])
		buttons.extend(['Назад'])
		return buttons

	def designer_order_validate_text(self, order):
		text = f'Заказ № {order.order_id} "{order.name}" \nДата добавления: {order.date}'
		if order.quantity > 1:
			text += f'\nКоличество экземпляров: {order.quantity}'
		if not (order.conditions == '' or order.conditions == None):
			text += f'\nУсловия эксплуатации: {order.conditions}' 
		if not (order.comment == '' or order.comment == None):
			text += f'\nКомментарий клиента: {order.comment}'
		return text

	order_validate_accept_time_btns = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']

	order_validate_accept_time_minutes_btns = ['5','10','15','20','25','30','35','40','45','50','55']