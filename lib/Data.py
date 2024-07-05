
class Data:

	def __init__(self):
		self.logical_statuses = {
			'prevalidate': 'ожидается предварительная валидация',
			'validate': 'ожидается валидация',
			'validated': 'валидирован',
			'parameters_set': 'цвет выбран',
			'waiting_for_item': 'ожидание предмета',
			'item_received': 'предмет в выдаче',
			'sample_aquired': '',
			'waiting_for_design': 'ожидание дизайнера'}

		self.physical_statuses = {
			'in_line': 'в очереди на печать',
			'printing': 'печатается',
			'finished': 'отпечатан',
			'in_pick-up': 'в пункте выдачи'}

		self.statuses = {}
		self.statuses.update(self.logical_statuses)
		self.statuses.update(self.physical_statuses)

		self.types = {
			'stl': 'stl файл',
			'link': 'модель из интернета',
			'sketch': 'печать по чертежу',
			'item': 'копия предмета',
			'production': 'мелкосерийное производство'}

		self.attributes = {
		    'name': 'название',
		    'type': 'тип',
		    'status': 'статус',
		    'comment': 'комментарий',
		    'priority': 'приоритет',
		    'completion_date': 'дата завершения',
		    'quantity': 'количество',
		    'color_id': 'цвет',
		    'assigned_designer_id': 'назначенный дизайнер',
		    'plastic_type': 'тип пластика',
		    'printer_type': 'тип принтера',
		    'layer_height': 'высота слоя',
		    'model_file': 'файл модели',
		    'link': 'ссылка',
		    'sketches': 'чертежи',
		    'price': 'цена',
		    'payed': 'оплачено',
		    'support_time': 'время удаления поддержек',
		    'prepayment_percent': 'процент предоплаты',
		    'support_remover': 'удалитель поддержек',
		    'pay_code': 'код оплаты',
		    'delivery_code': 'код доставки',
		    'delivery_user_id': 'назначенный доставщик'
		}


# str
#  'name', 'comment', 'link'

# int
#  'priority','quantity','price','payed','support_time','prepayment_percent','pay_code','delivery_code','completion_date'

# float
#  layer_height

# selection
#  'type','status','assigned_designer_id','plastic_type','printer_type','support_remover','delivery_user_id '

# other
#  model_file
#  sketches

#  color_id