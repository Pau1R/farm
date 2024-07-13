class Order_text:
	def __init__(self, app, chat):
		self.app = app
		self.chat = chat

	def get_text(self, order):
		data = self.app.data

		# set parameters
		free_start = order.is_free_start()
		prepayed = order.is_prepayed()
		
		# convert order status to readable format
		status = order.logical_status
		if not status:
			status = order.physical_status
		delivery_text = 'Код передачи/получения'
		if self.chat.is_employee:
			status = data.statuses[status]
		else:
			logical = order.logical_status
			physical = order.physical_status
			if logical in ['prevalidate','validate']:
				status = 'Ожидание дизайнера'
			elif logical == 'validated':
				status = 'Ожидание действий клиента'
			elif logical == 'parameters_set':
				status = 'Ожидание оплаты'
			# statuses for item order
			elif logical == 'waiting_for_item':
				status = 'Принесите предмет в пункт выдачи'
				delivery_text = 'Код передачи'
			elif logical in ['sample_aquired','waiting_for_design']:
				status = 'Ожидание дизайнера'
			elif logical == 'client_check':
				status = 'Ожидание действий клиента'
			# physical statuses
			elif physical == 'in_line':
				status = 'В очереди на печать'
			elif physical == 'printing':
				status = 'Печатается'
			elif physical == 'finished':
				status = 'Печать завершена'
			elif physical == 'in_pick-up':
				status = 'В пункте выдачи'
				delivery_text = 'Код получения'
			else:
				status = data.statuses[status]

		# prepare data
		name = order.name
		id = order.id
		status = status.upper()
		delivery_code = order.delivery_code
		created = self.app.functions.russian_date(order.created)
		price = order.price
		quantity = order.quantity
		quality = data.quality[order.quality]
		weight = int(order.weight) * quantity
		total_weight = int(order.weight) * quantity
		plastic_type = order.plastic_type
		if plastic_type == 'basic':
			plastic_type = 'любой базовый'
		plastic_type.lower()
		color_id = order.color_id
		color = self.app.equipment.color_logic.get_color_name(order.color_id)
		if color:
			color = color.lower()
		completion_date = self.app.functions.russian_date(order.completion_date)
		support_time = int(order.support_time)
		support_remover = 'клиент' if order.support_remover == 'Клиент' else 'студия'
		payed = int(order.payed)
		prepayment_price = int(order.get_prepayment_price())
		if payed:
			if not free_start and not prepayed:
				prepayed = f'Предоплачено: {payed}/{prepayment_price} рублей'
			else:
				prepayed = f'Предоплачено: {payed} рублей'
		else:
			prepayed = 'Предоплачено: 0 рублей'
		comment = order.comment
		chat = self.app.get_chat(order.user_id)
		user_name = chat.user_name
		user_id = chat.user_id
		type_ = data.types[order.type]
		priority = order.priority
		confirmed = ''
		if order.type == 'sketch':
			confirmed = 'нет'
			if order.confirmed:
				confirmed = 'да'
		designer_user_name = self.app.get_chat(order.designer_id)
		if designer_user_name:
			designer_user_name = designer_user_name.user_name
		printer_type_name = self.app.printer_type_logic.get_printer_type(order.printer_type)
		if printer_type_name:
			printer_type_name = printer_type_name.name
		layer_height = order.layer_height
		model_file = order.model_file
		link = order.link
		sketches = len(order.sketches)
		prepayment_percent = int(order.prepayment_percent)
		pay_code = order.pay_code
		delivery_user_name = self.app.get_chat(order.delivery_user_id)
		if delivery_user_name:
			delivery_user_name = delivery_user_name.user_name
		miscellaneous = order.miscellaneous

		# set admin text
		if self.chat.is_admin():
			text = f'{id}: {name}\n\n'
			text += f'Клиент: {user_name} (id: {user_id})\n'
			text += '\n--- Общие ---\n'
			text += f'Тип заказа: {type_}\n'
			text += f'Статус: {status}\n'
			text += f'Комментарий: {comment}\n'
			text += f'Приоритет: {priority}\n'
			if confirmed:
				text += f'Подтвержден клиентом: {confirmed}\n'
			text += f'Дата готовности (примерно): {completion_date}\n'
			text += f'Кол-во экземпляров: {quantity}\n'
			text += f'Качество: {quality}\n'
			text += f'Вес экземпляра: {weight} грамм\n'
			text += f'Цвет изделия: {color}\n'
			text += f'Назначенный дизайнер: {designer_user_name}\n'
			text += f'Дополнительная информация: {miscellaneous}\n'
			text += '\n--- Настройки печати ---\n'
			text += f'Тип материала: {plastic_type}\n'
			text += f'Тип принтера: {printer_type_name}\n'
			text += f'Высота слоя: {layer_height}\n'
			text += '\n--- Файлы, ссылка, фото ---\n'
			if model_file:
				text += 'stl файл: 1\n'
			else:
				text += 'stl файл: 0\n'
			if link:
				text += 'Ссылка: 1\n'
			else:
				text += 'Ссылка: 0\n'
			text += f'Чертежы/фото: {sketches}\n'
			text += '\n--- Финансы ---\n'
			text += f'Стоимость: {price} рублей\n'
			text += f'{prepayed}\n'
			text += f'Время удаления поддержек c 1 шт.: {support_time}\n'
			text += f'Процент предоплаты: {prepayment_percent}\n'
			text += f"Удаление поддержек: {support_remover}\n"
			text += '\n--- Доставка ---\n'
			text += f'Код оплаты: {pay_code}\n'
			text += f'{delivery_text}: {delivery_code}\n\n'
			text += f'Точка выдачи: {delivery_user_name}\n'

		# set designer text
		elif self.chat.is_designer():
			text = f'{id}: {name}\n\n'
			text += f'Тип заказа: {type_}\n'
			text += f'Статус: {status}\n'
			text += f'Дата создания: {created}\n'
			if priority:
				text += f'Приоритет: {priority}\n'
			if color_id:
				text += f'Цвет изделия: {color}\n'
			if quantity > 1:
				text += f'Кол-во экземпляров: {quantity}\n'
			text += f'Качество: {quality}\n'
			if printer_type_name:
				text += f'Тип принтера: {printer_type_name}\n'
			if plastic_type:
				text += f'Тип материала: {plastic_type}\n'
			if weight:
				text += f'Вес экземпляра: {weight} грамм\n'
			if layer_height:
				text += f'Высота слоя: {layer_height}\n'
			if support_time:
				text += f'Время удаления поддержек c 1 шт.: {support_time}\n'
			if comment:
				text += f'Комментарий: {comment}\n'
			if miscellaneous:
				text += f'Дополнительная информация: {miscellaneous}\n'
		
		# set client text
		elif not self.chat.is_employee:
			text = ''
			text = name + '\n\n'
			text += f'Статус: {status}\n'
			if delivery_code and delivery_text:
				text += f'{delivery_text}: {delivery_code}\n\n'
			text += f'Дата создания: {created}\n'
			if priority:
				text += f'Приоритет: {priority}\n'
			if price:
				text += f'Стоимость: {price} рублей\n'
			if quantity > 1:
				text += f'Кол-во экземпляров: {quantity}\n'
			text += f'Качество: {quality}\n'
			if total_weight:
				text0 = 'Общий вес' if quantity else 'Вес'
				text += f'{text0}: {total_weight} грамм\n'
			if plastic_type:
				text += f'Тип материала: {plastic_type}\n'
			if color_id:
				text += f'Цвет изделия: {color}\n'
			if completion_date:
				text += f'Дата готовности (примерно): {completion_date}\n'
			if support_time:
				text += f"Удаление поддержек: {support_remover}\n"
			if prepayed:
				text += f'{prepayed}\n'
			if comment:
				text += f'Комментарий: {comment}\n'
		return text