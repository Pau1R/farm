class Texts:
	chat = None
	address = ''

	def __init__(self, chat, address):
		self.chat = chat

#---------------------------- ADMIN TEXTS ----------------------------

	spool_diameter = 1.75
	spool_types = ['PLA', 'PETG', 'ABS', 'PC', 'TPE']
	spool_densities = [1.24, 1.27, 1.04, 1.2, 1.2]

	spool_weight = ['0.1 кг', '0.5 кг', '0.7 кг', '0.9 кг', '1 кг', '2 кг', '2.5 кг', '3 кг']

	spool_colors = ['белый', 'черный', 'темно-серый', 'серый', 'светло-серый']
	spool_colors.extend(['красный', 'оранжевый', 'жёлтый', 'зелёный', 'голубой', 'синий', 'фиолетовый'])

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