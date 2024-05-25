class Settings:
	app = None

	settings = {}
	names = ['support_remove_price',
		'prepayment_percent',
		'prepayment_free_max',
		'phone_number',
		'card_number', 
		'account_number',
		'transfer_receiver']
		# TODO: add new setting for plastic types

	def __init__(self, app):
		self.app = app
		settings = self.app.db.get_settings()
		for name in self.names:
			if not name in settings:  # add to db
				self.app.db.add_setting(name, '')
				settings[name] = ''
		for name in settings:
			if not name in self.names:  # remove from db
				self.app.db.remove_setting(name)
		self.settings = settings

	def get(self, name):
		return self.settings[name]

	def set(self, name, value):
		self.settings[name] = value
		self.app.db.update_setting(name, value)