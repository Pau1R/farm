# CLIENT TEXTS

class Texts:
	app = None

	def __init__(self, app):
		self.app = app

	top_menu = 'Выберите действие'
	order_menu = 'Выберите тип заказа'
	
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
"""

	model_name = 'Напишите название вашей модели'

	model_quantity = 'Сколько экземпляров вам нужно?'
	model_quantity_buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

	model_conditions = 'В каких условиях будет эксплуатироваться модель?'
	model_conditions_buttons = ['в доме', 'на улице', 'в автомобиле', 'не знаю']

	supported_3d_extensions = ['stl', 'obj', 'step', 'svg', '3mf', 'amf']

	file = 'Загрузите свой 3д файл. Поддерживаются следующие форматы: ' + ', '.join(supported_3d_extensions)

	supports_btns = [['Да, сам уберу', 'client'], ['Нет, уберите вы', 'seller']]
		
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

	prepayment_successful = 'Предоплата успешно внесена! Заказ принят в работу.\n\nОплатить полную стоимость заказа вы сможете наличными при получении заказа либо переводом.'

	order_design_start = 'Разработка 3д модели начата'
	order_design_end = 'Разработка 3д модели завершена'
	
	order_print_start = 'Распечатка заказа начата'
	order_print_end = 'Распечатка заказа окончена'

	def order_at_pickup(self, pickup_id): 
		text = f'Заказ готов к выдаче. При получении сообщите номер {pickup_id}.'
		return text
