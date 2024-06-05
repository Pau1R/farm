# CLIENT TEXTS

class Texts:
	app = None

	def __init__(self, app):
		self.app = app

	model_quantity = 'Сколько экземпляров вам нужно?'
	model_quantity_buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

	model_conditions = 'В каких условиях будет эксплуатироваться модель?'
	model_conditions_buttons = ['в доме', 'на улице', 'в автомобиле', 'не знаю']

	supported_3d_extensions = ['stl', 'obj', 'step', 'svg', '3mf', 'amf']

	file = 'Загрузите свой 3д файл. Поддерживаются следующие форматы: ' + ', '.join(supported_3d_extensions)