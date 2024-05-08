import configparser
import os

class Conf:
	bot_token = ''
	roles = {
		'owner': 'Владелец',
		'admin': 'Администратор',
		'operator': 'Оператор',
		'designer': 'Дизайнер',
		'issue': 'Выдача'
	}

	def __init__(self):
		config = configparser.ConfigParser()
		config.read("config.ini")

		if os.path.exists('bot.dev'):
		    self.bot_token = config['Bot']['bot_dev_token'] # dev
		else:
		    self.bot_token = config['Bot']['bot_prod_token'] # prod
