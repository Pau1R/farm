from lib.employees.Employee import Employee
from lib.clients.Client import Client

class Chat:
    app = None
    user_id: str
    is_employee = False
    created = None
    get_employed = False
    user = None

    def __init__(self, app, user_id, isEmployee, created):
        self.app = app
        self.user_id = user_id
        self.is_employee = isEmployee
        self.created = created

        self.create_user()

    def new_message(self, message):
        # if message.text == '/start':
        #     self.user = None
        if self.user == None:
            self.create_user()
        self.user.new_message(message)

    def create_user(self):
        if self.is_employee:
            self.user = Employee(self.app, self)
        else:
            self.user = Client(self.app, self)

    def become_employee(self):
        self.is_employee = True
        self.get_employed = False