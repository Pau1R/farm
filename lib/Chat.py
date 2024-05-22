from lib.employee.Employee import Employee
from lib.client.Client import Client
from lib.Gui import Gui

class Chat:
    app = None
    GUI = None
    message = None
    user_id: str
    is_employee = False
    created = None
    get_employed = False
    user = None
    context = ''
    message_pause = None

    def __init__(self, app, user_id, isEmployee, created):
        self.app = app
        self.user_id = user_id
        self.is_employee = isEmployee
        self.created = created
        self.GUI = Gui(app, self, '-1')

        self.create_user()

    def new_message(self, message):
        self.GUI.clear_chat()
        self.message = message

        if self.user == None:
            self.create_user()

        if message.file1 == '-1' and message.function == '1':
            self.process_warn_user()
            return
        elif self.context.startswith('~'):
            if message.type == 'button':
                self.show_warn_user()
            else:
                self.special_format()
        elif message.type == 'button':
            self.message.data_to_special_format(self.message.data)
            self.user.new_message(self.message)
        elif self.context.startswith('secret_message~'):
            self.special_format()
        else:
            self.user.new_message(message)

    def special_format(self):
        self.message.data_to_special_format(self.context)
        self.context = ''
        self.user.new_message(self.message)

    def create_user(self):
        if self.is_employee:
            self.user = Employee(self.app, self)
        else:
            self.user = Client(self.app, self)

    def become_employee(self):
        self.is_employee = True
        self.get_employed = False
        name = self.user.name
        self.create_user()
        self.user.name = name

    def set_context(self, address, function):
        self.context = '~' + address + '|' + str(function) + '||'

    def show_warn_user(self):
        self.message_pause = self.message
        text = 'Ожидается ввод данных, отменить нажатие кнопки?'
        buttons = [['Да, отменить, я хочу ввести данные', 'stop'], ['Нет, выполнить действие кнопки', 'continue']]
        self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

    def process_warn_user(self):
        if self.message.btn_data == 'continue':
            self.context = ''
            self.message.file1 = ''
            self.new_message(self.message_pause)
            self.message_pause = None