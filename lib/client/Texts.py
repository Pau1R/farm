# CLIENT TEXTS

class Texts:
	app = None

	def __init__(self, app):
		self.app = app

	top_menu = 'Выберите действие'
	order_menu = 'Выберите тип заказа'

	top_menu_buttons = [['Сделать заказ', 'order']]
	top_menu_buttons.append(['Информация о студии', 'info'])
	
	order_buttons = [['Выбрать готовую модель из каталога', 'farm model']]
	order_buttons.append(['Распечатать мою модель', 'user model'])
	order_buttons.append(['Создать и распечатать модель по моему чертежу', 'user drawing'])

	info_text = """
-------- пункт выдачи ------------------
г. Стерлитамак, ул. Сакко и Ванцетти, 63, "Бизнес-контакт".
График работы: ежедневно с 9:00 до 21:00.
	
-------- доставка ----------------------
По странам СНГ службой boxberry за счет клиента

-------- технология печати -------------
Печать одноцветная на fdm принтерах.

-------- используемые принтеры ---------
1) bambu lab p1s
2) creality ender 3 s1 pro

-------- используемые материалы --------
1) PLA
2) PETG
3) PC (поликарбонат)
"""

	model_name = 'Напишите название вашей модели'

	model_quantity = 'Сколько экземпляров вам нужно?'
	model_quantity_buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

	model_conditions = 'В каких условиях будет эксплуатироваться модель?'
	model_conditions_buttons = ['в доме', 'на улице', 'в автомобиле', 'не знаю']

	model_comment = 'Напишите комментарий'

	supported_3d_extensions = ['stl', 'obj', 'step', 'svg', '3mf', 'amf']

	file = 'Загрузите свой 3д файл. Поддерживаются следующие форматы: ' + ', '.join(supported_3d_extensions)

	wait_for_designer = 'Ваш файл передан дизайнеру для оценки, ожидайте.'

	def price_text(self, order_id):
		order = None
		for entry in self.app.orders:
			if entry.order_id == order_id:
				order = entry
		if order == None:
			return
		text = f'Модель "{order.name}"\n\n'
		if order.plastic_color == '':
			text += f'Предварительная стоимость: {order.price} rub\n'
		else:
			text += f'Итоговая стоимость: {order.price} rub\n'
		if order.quantity > 1:
			text0 = 'Общий вес'
		else:
			text0 = 'Вес'
		text += f'{text0}: {int(order.weight) * order.quantity} грамм\n'
		if order.quantity > 1:
			text += f'Кол-во экземпляров: {order.quantity}\n'
		text += f'Время, необходимое для печати'
		if order.time > 119:
			text += f' (часов): {int(order.time/60)}'
		else:
			text += f': {int(order.time/60)} минут'
		if order.start_time_estimate != None:
			text += f'\nНачало печати (приблизительно): {order.start_time_estimate}'
		if order.support_remover != '':
			text += f'\nУдаление поддержек: {order.support_remover}'
		else:
			if order.support_time > 0:
				text0 = f'\nСтоимость удаления поддержек нами'
				if order.quantity > 1:
					text0 += ' со всех экземпляров'
				text += f'\n{text0}: {int(order.support_time * order.quantity * self.app.support_remove_price)} rub'
		if order.prepayed > 0:
			text += f'Предоплата: внесено {order.prepayed} rub.\n'
			if order.prepayed < order.prepayment_percent * order.price:
				text += f'\n\nПредоплата внесена не полностью, заказ не принят в работу!'
		return text

	supports_btns = [['Да, сам уберу', 'client'], ['Нет, уберите вы', 'seller']]

	price_btns = [['Согласен, перейти к предоплате', 'confirm'], ['Отменить заказ', 'cancel']]
	
	# available_materials = 'Пока ведется оценка вы можете ознакомиться с доступными материалами и определиться с цветом изделия.'
	
	def confirm_prepayment(self, model, print, ready):
		text = f'Предварительная стоимость заказа: {model + print} рублей\n'
		if model != 0:
			text += f'- разработка 3д модели: {model} рублей\n- печать: {print} рублей\n'
		text += 'Точная стоимость будет известна после разработки 3д модели.\n'
		text += f'Предварительный срок готовности: {ready}' # 10.04.2024
		return text

	confirm_prepayment_buttons = [['Согласен, внести предоплату', 'Continue'], ['Отменить заказ', 'Cancel']]

	def prepayment_instructions(self, price, payer_id):
		text = f'Размер предоплаты: {price} рублей.\n'
		text += f'Для внесения предоплаты сделайте перевод на карту сбербанка по номеру телефона указанному ниже. В комментарии к переводу обязательно укажите ваш номер покупателя: {payer_id}\n'
		text += 'После зачисления средств вам прийдет уведомление о принятии заказа в работу.'
		return text

	payment_phone_number = '+71231234567'

	prepayment_successful = 'Предоплата успешно внесена! Заказ принят в работу.\n\nОплатить полную стоимость заказа вы сможете наличными при получении заказа либо переводом.'

	order_design_start = 'Разработка 3д модели начата'
	order_design_end = 'Разработка 3д модели завершена'
	
	order_print_start = 'Распечатка заказа начата'
	order_print_end = 'Распечатка заказа окончена'

	def order_at_pickup(self, pickup_id): 
		text = f'Заказ готов к выдаче. При получении сообщите номер {pickup_id}.'
		return text
