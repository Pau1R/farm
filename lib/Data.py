
class Data:

	def __init__(self):
		self.logical_statuses = {
			'prevalidate': 'ожидание предварительной валидации',
			'validate': 'ожидание валидации',
			'validated': 'валидирован',
			'parameters_set': 'ожидание оплаты',
			'client_check': 'ожидание подтверждения клиентом',
			'clarify': 'ожидание дизайнера',
			'waiting_for_item': 'ожидание предмета',
			'item_received': 'предмет в выдаче',
			'sample_aquired': 'предмет у студии',
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
		    'confirmed': 'подтвержден клиентом',
		    'completion_date': 'дата завершения',
		    'quantity': 'количество',
		    'quality': 'качество',
		    'weight': 'вес экзмепляра',
		    'color_id': 'цвет',
		    'designer_id': 'назначенный дизайнер',
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
		    'delivery_user_id': 'назначенный доставщик',
		    'miscellaneous': 'информация'
		}

		self.plastics = ['']

		self.supported_files = ['stl', 'obj', 'step', 'svg', '3mf', 'amf']

		self.quality = {
			'cheap': 'максимально дешевое',
		    'optimal': 'оптимальное цена/качество',
		    'quality': 'максимальное качество',
		    'durability': 'максимальная прочность',
		}

# str
#  'name', 'comment', 'link'

# int
#  'priority','quantity','price','payed','support_time','prepayment_percent','pay_code','delivery_code','completion_date'

# float
#  layer_height

# selection
#  'type','status','designer_id','plastic_type','printer_type','support_remover','delivery_user_id'

# частные случаи:
#  model_file
#  sketches
#  color_id
# 'completion_date'