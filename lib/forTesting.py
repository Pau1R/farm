# class Dog:
#     def bark(self, cat):
#         cat.name = 'bro'
#         cat.changeName()
#         print(cat.name)

# class Pig:
#     def oink(self, cat):
#         cat.name = 'hru'
#         print(cat.name)

# class Cat:
#     name = 'tom'
#     def callAll(self):
#         Dog().bark(self)
#         Pig().oink(self)
#         # dog.bark(self)
#     def sayName(self):
#         print(self.name)
#     def changeName(self):
#         self.name = 'third name'

# cat = Cat()
# cat.callAll()
# cat.sayName()

# class Cat:
#     def first(self):
#         print('first')
#     def second(self):
#         self.first()

# cat = Cat()
# cat.second()


# class Spool:
# 	color = ''
# 	weight = ''
# 	type = ''

# 	def __init__(self, color, weight, type):
# 		self.color = color
# 		self.weight = weight
# 		self.type = type


# spool1 = Spool('red', 1000, 'pla')
# spool5 = Spool('red', 1000, 'pla')
# spool2 = Spool('blue', 1000, 'petg')
# spool3 = Spool('red', 1000, 'petg')
# spool4 = Spool('green', 1000, 'petg')
# spools = [spool1, spool2, spool3, spool4, spool5]

# class Order:
# 	plastic_type = ''
# 	plastic_color = ''
# 	weight = 0

# 	def __init__(self, color, weight, type):
# 		self.plastic_color = color
# 		self.weight = weight
# 		self.plastic_type = type

# order1 = Order('blue', 10000, 'petg')
# order2 = Order('red', 100, 'pla')

# orders = [order1, order2]

# diction = {}
# for spool in spools:
# 	if spool.type not in diction:
# 		# add spool type
# 		diction[spool.type] = {spool.color: ''}
# 	else:
# 		# add spool color
# 		if spool.color not in diction[spool.type]:
# 			mini = diction[spool.type].copy()
# 			mini.update({spool.color: ''})
# 	# add spool weight
# 	mini = diction[spool.type]
# 	if spool.color in mini:
# 		previous_weight = mini[spool.color]
# 		if previous_weight == '':
# 			previous_weight = 0
# 	mini.update({spool.color: previous_weight + spool.weight})

# print(diction)



# for order in orders:
# 	mini = diction[order.plastic_type]
# 	weight = 0
# 	if order.plastic_color in mini:
# 		weight = mini[order.plastic_color]
# 	mini[order.plastic_color] = weight - order.weight
# 	if order.weight >= weight:
# 		del mini[order.plastic_color]
# print(type(diction))

# print( isinstance(diction,dict))

from datetime import datetime
cat = 'None'

print(datetime.strptime(cat, '%m/%d/%y %H:%M:%S'))