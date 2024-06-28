from lib.employee.Employee import Employee
from lib.client.Client import Client
from lib.Gui import Gui
from datetime import date

class Chat:
    
    def __init__(self, app, user_id, name, isEmployee, created):
        self.app = app
        self.user_id = user_id
        self.user_name = name
        self.is_employee = isEmployee
        self.created = created
        self.GUI = Gui(app, self, '-1')
        self.message = None
        self.context = ''
        self.message_pause = None
        self.last_access_date = date.today()
        self.user = None
        self.get_employed = False
        
        self.create_user()

    def new_message(self, message):
        self.GUI.clear_chat()
        self.message = message

        if not self.user:
            self.create_user()

        if message.file1 == '-1' and message.function == '1':
            self.process_warn_user()
        elif self.context.startswith('~'):
            self.handle_context_message()
        elif message.type == 'button':
            self.button_format()
        elif self.context.startswith('secret_message~'):
            self.special_format()
        else:
            self.user.new_message(message)

    def handle_context_message(self):
        data = self.message.data.split('|')
        context = self.context.split('|')
        if self.message.type == 'button' and not (data[0] == context[0] and data[1] == context[1]):
            self.show_warn_user()
        else:
            self.button_format() if self.message.type == 'button' else self.special_format()

    def button_format(self):
        self.message.data_to_special_format(self.message.data)
        self.user.new_message(self.message)

    def special_format(self):
        self.message.data_to_special_format(self.context)
        self.context = ''
        self.user.new_message(self.message)

    def create_user(self):
        self.user = Employee(self.app, self) if self.is_employee else Client(self.app, self)

    def become_employee(self):
        self.is_employee = True
        self.get_employed = False
        name = self.user_name
        self.create_user()
        self.user_name = name
        self.app.db.update_chat(self)

    def set_context(self, address, function):
        self.context = f'~{address}|{function}||'

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

    def next_level_id(self, chat):
        message = chat.message
        level = len(chat.address.split('/'))
        if level == 1:
            return message.file2
        elif level == 2:
            return message.file3
        elif level == 3:
            return message.file4
        elif level == 4:
            return message.file5
        elif level == 5:
            return message.file6

    def add_if_text(self, chat):
        message = chat.message
        file = self.next_level_id(chat)
        if message.type in ['text', 'document', 'photo'] and message.text != '/start' and not file:
            chat.GUI.messages_append(message)

    def not_repeated_button(self, chat):
        data = chat.message.data
        if not data or data != chat.last_data:
            chat.last_data = data
            return True
        return False