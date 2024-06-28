from datetime import timedelta
from datetime import datetime
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

	def russian_date(self, date_):
		if date_ == None:
			return ''
		if isinstance(date_, datetime):
			date_ = date_.date()
		if date_ == date.today():
			return 'сегодня'
		elif date_ == date.today() + timedelta(days=1):
			return 'завтра'
		elif date_ == date.today() + timedelta(days=2):
			return 'послезавтра'
		elif date_ == date.today() - timedelta(days=1):
			return 'вчера'
		elif date_ == date.today() - timedelta(days=2):
			return 'позавчера'
		else:
			return str(date_.day) + ' ' + self.months[date_.month]

	def russian_date_2(self, date_):
		if date_ < date.today():
			return 'задержка'
		else:
			return self.russian_date(date_)

	def get_weight_string(self, weight):
	    if weight % 1000 == 0:
	        return str(weight // 1000) + ' кг'
	    else:
	        weight_str = '{:.2f}'.format(weight / 1000).rstrip('0').rstrip('.')
	        return weight_str + ' кг'

	def get_next_free_id(self, array):
		ids = []
		for elem in array:
			ids.append(int(elem.id))
		ids.sort()
		id = 1
		for elem in ids:
			if elem == id:
				id += 1
			else:
				break
		return id

functions = Functions()

# print(functions.russian_date(date.today()))