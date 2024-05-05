import json
from config import bot_config
import datetime
from os import path as osPath
# Telegram api
import telebot
from telebot import types

JSON_FOLDER = "json_file"
file_names = {
    "schedule":"schedule.json",
    "notes":"notes.json"
}
today = datetime.datetime.today().weekday()

def save(filename:str, text:str): 
    path = osPath.join(JSON_FOLDER,file_names[filename])
    with open(path,"w",encoding="utf-8") as file:
        json.dump(text,file, sort_keys=False,indent=4,ensure_ascii=False)

def load(filename:str) -> dict:
    path = osPath.join(JSON_FOLDER,file_names[filename])
    with open(path, "r",encoding="utf-8") as file:
        result = json.load(file)
    return result
# refactored save and load

Notes = load("notes")
Schedule = load("schedule")
# here and everywhere else, those two files are no longer loading EVERY time from file

week = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресение"
}
class Bot():
    def __init__(self,token) -> None:

        """
        I refactored this entire bot to be a class. 
        
        To add new handlers - write new method with a doc string
        (
        doc string is a string, that appears right after function declaration.
        like this:

        def func():
            'THIS IS A DOC STRING'

        )

        For a 'pure handler' (one which doesn't use states), 
        doc string will be used as a text on the InlineKeyboardButton

        For a 'state handler' (one which does use states),
        doc string will be used as a key for states dictionary check when recieving message

        States themselves are refactored to be a dictionary of dictionaries.
        If you need to add new possible states, add a new key with it's one word description
        as a key. This key then can be used in your 'state handlers'.

        If you need to add some helper method that isn't a handler and it needs a doc string
        just make sure that doc string contains word 'help', otherwise it could be detected as
        pure handler
        """

        self.bot = telebot.TeleBot(token)
        self.states = { 
            "create":{},
            "edit":{},
            "delete":{},
            "read":{}
        }
        self.methods = [func for attr in dir(self) if callable(func:=getattr(self, attr)) and not attr.startswith("__") ]
        self.pure_handlers = [self.bot.message_handler(commands=[method.__name__])(method) for method in self.methods if method.__doc__ and not("help" in method.__doc__ or "handle" in method.__name__)]
        self.state_handlers = [self.bot.message_handler(func=lambda message:self.states[method.__doc__].get(message.chat.id,False))(method) for method in self.methods if method.__name__.endswith("handler")]
        self.callback_func_dict = {k:v for k,v in zip([method.__name__ for method in self.pure_handlers],self.pure_handlers)}
        self.bot.callback_query_handler(func=lambda call: True)(self.handle_callback_query)

    def run(self):
        self.bot.infinity_polling()

    def start(self,message):
        markup = types.InlineKeyboardMarkup(row_width=3)
        text_list = [method.__doc__ for method in self.pure_handlers] # all texts
        callback_list = [method.__name__ for method in self.pure_handlers] # all callbacks
        # create a list of inline keyboard buttons for each text and callback, then unpack it as arguments for markup.add
        markup.add(*[types.InlineKeyboardButton(text,callback) for text,callback in zip(text_list,callback_list)])
        self.bot.send_message(message.chat.id, PROMPTS["start"], reply_markup=markup)

    def help(self,message):
        "help"
        self.bot.send_message(message.chat.id, PROMPTS["help"])

    def create_note(self,message):
        "create note"
        self.bot.send_message(message.chat.id, PROMPTS["create"])
        self.states["create"][message.chat.id] = True

    def edit_note(self,message):
        "edit note"
        self.bot.send_message(message.chat.id, PROMPTS["edit"])
        self.states["edit"][message.chat.id] = True

    def delete_note(self,message):
        "delete note"
        self.bot.send_message(message.chat.id, PROMPTS["delete"])
        self.states["delete"][message.chat.id] = True

    def read_note(self,message):
        "read note"
        self.bot.send_message(message.chat.id, PROMPTS["read"])
        self.states["read"][message.chat.id] = True

    def list_note(self,message):
        "list note"
        Notes_names = "\n".join(Notes.keys())
        self.bot.send_message(message.chat.id, Notes_names)

    def change_week_parity(self,message):
        "change week parity"
        Schedule[2] = int(not Schedule[2]) # 0 -> 1 ; 1 -> 0
        save("schedule", Schedule)
        self.bot.send_message(message.chat.id, PROMPTS["change_parity"]) # parity complite -> parity changed

    def schedule(self,message):
        "schedule"
        fri,sat,sun = week[4],week[5],week[6]
        week_parity = int(not Schedule[2]) # 0 -> 1 ; 1 -> 0
        day_Schedule = lambda day,parity=week_parity: "\n".join([" | ".join(lesson) for lesson in Schedule[parity][week[day]]])
        if week[today] in [sat,sun]:
            Schedule_output += PROMPTS["schedule_monday"] + "\n\n" + day_Schedule(week[0],not week_parity)
            self.bot.send_message(message.chat.id, Schedule_output)
            return
        Schedule_output = PROMPTS["schedule_today"] + "\n\n"
        Schedule_output += day_Schedule(today)
        if week[today] == fri:
            Schedule_output += PROMPTS["schedule_monday"] + "\n\n" + day_Schedule(week[0],not week_parity)
        self.bot.send_message(message.chat.id, Schedule_output)
        # total refactoring, god was it awful before

    # handlers
        
    def create_handler(self,message):
        "create"
        if "@" in message.text:
            name, text = message.text.split("@")
            Notes[name] = text
            save("notes",Notes)
            result = PROMPTS["success_create"]
            self.states["create"][message.chat.id] = False
        else:
            result = PROMPTS['failure_create']
        self.bot.send_message(message.chat.id, result)
        # moved out of branches

    def edit_handler(self,message): #edite_handler -> edit_handler
        "edit"
        # Эта функция нужна для создания заметок. Учитывайте что он записывает словарь!
        result = PROMPTS["failure_edit"]
        if "@" in message.text:
            name, text = message.text.split('@')
            if name in Notes.keys():
                Notes[name] = text
                save("notes",Notes)
                result = PROMPTS["success_edit"]
        self.bot.send_message(message.chat.id, result)
        self.states["edit"][message.chat.id] = False 
        # moved stuff out of branches

    def delete_handler(self,message):
        "delete"
        name = message.text
        if name in Notes:
            Notes.remove(name) #pop -> remove
            result = PROMPTS["success_delete"]
            save("notes",Notes)
        else:
            result = PROMPTS["failure_delete"]
        self.bot.send_message(message.chat.id, result)
        self.states["delete"][message.chat.id] = False
        # moved stuff out of branches

    def read_handler(self,message): # watch_handler -> read_handler
        "read"
        name = message.text
        self.bot.send_message(message.chat.id, Notes[name] if name in Notes else PROMPTS["failure_read"]) # "Вы написали неправильно название заметки." -> "Неправильное название заметки."
        self.states["read"][message.chat.id] = False
        # refactored a little
    
    # callbacks
        
    def handle_callback_query(self,call):
        self.callback_func_dict[call.data](call.message)

PROMPTS = {
    "start":'Привет, этот бот был создан для просмотра расписания и создание заметок. (Примечание заметки не имеют возможности хранить фото)',
    "help":"Commands for bot: \n/" + " ({})\n/".join([func.__name__ for attr in dir(Bot) if callable(func:=getattr(Bot, attr)) and not attr.startswith("__") and func.__doc__ and not("help" in func.__doc__ or "handle" in func.__name__) ]),
    "create":"Напишите название и укажите '@' в конце названия новой заметки. После знака собаки все написанное будет записанно в заметку это должно выглядеть так:\n 'Название@Заметка.'",
    "edit":"Напишите название заметки. После написание название напишите @ после которого можно написать новое содержание заметки.",
    "delete":"Напишите название заметки для того чтобы удалить заметку.",
    "read":"Напишите название заметки для того чтобы увидеть содержание заметки.",
    "change_parity":"parity changed",
    "schedule_today":"Расписание на сегодня",
    "schedule_monday":"Расписание на понедельник",
    "success_create":"Заметка сохранена",
    "success_edit":"Изменения сохранены",
    "success_delete":"Удаление произошло",
    "failure_create":"Название заметки должно заканчиваться на '@' иначе произойдет неправильное сохранение.",
    "failure_edit":"Вы неправильно написали изменения заметки. Вид изменения заметок: '<Название>@<Новое содержание заметки>'.",
    "failure_delete":"Вы написали неправильно название заметки.",
    "failure_read":"Неправильное название заметки.",
}
help_descriptions = (
    "Для того чтобы увидеть рассписание на сегодня и на завтра",
    "для создание заметки нужно следовать такой конструкции 'название@заметка'",
    "Показывает все note в виде списка в котором можно выбрать заметку для отображени.",
    "После написание команды нужно написать 'название@измененная заметка'",
    "для удаление заметки вам нужно после ввода команды написать название заметки",
    "после ввода нужно написать название заметки"
)
PROMPTS["help"] = PROMPTS["help"].format(*help_descriptions)
# I just like to do something like this:
if __name__ == "__main__": 
    bot = Bot()
    try:
        bot.run()
    except KeyboardInterrupt:quit()
