from datetime import date

class Functions:
	months = {
		1:'января',
		2:'февраля',
		3:'марта',
		4:'апреля',
		5:'мая',
		6:'июня',
		7:'июля',
		8:'августа',
		9:'сентября',
		10:'октября',
		11:'ноября',
		12:'декабря'}

	def russian_date(self, date):
		if date == None:
			return ''
		elif date.day == date.today().day and date.month == date.today().month:
			return 'сегодня'
		else:
			return str(date.day) + ' ' + self.months[date.month]

	def russian_date_2(self, date_):
		if date_ < date.today():
			return 'задержка'
		else:
			return self.russian_date(date_)

	def get_weight_string(self, weight):
	    if weight % 1000 == 0:
	        return str(weight // 1000) + 'кг'
	    else:
	        return '{:.2f}кг'.format(weight / 1000)

functions = Functions()

# print(functions.russian_date(date.today()))