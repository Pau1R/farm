
class Data:

	def __init__(self):
		self.statuses = {
		    'prevalidate': 'ожидается предварительная валидация',
		    'validate': 'ожидается валидация',
		    'validated': 'валидирован',
		    'parameters_set': 'цвет выбран',
		    'waiting_for_item': 'ожидание предмета',
		    'item_received': 'предмет в выдаче',
		    'sample_aquired': '',
		    'waiting_for_design': 'ожидание дизайнера'}

		self.statuses.update({
		    'in_line': 'в очереди на печать',
		    'printing': 'печатается',
		    'finished': 'отпечатан',
		    'in_pick-up': 'в пункте выдачи'
		})

		self.types = {
		    'stl': 'stl файл',
		    'link': 'модель из интернета',
		    'sketch': 'печать по чертежу',
		    'item': 'копия предмета',
		    'production': 'мелкосерийное производство'}