import json
from config import bot_config
import datetime

# Telegram api
import telebot
from telebot import types

# Переменные
bot = telebot.TeleBot(bot_config['Token'])
path_schedule = "json_file/schedule.json"
path_notes = "json_file/notes.json"
state = {} 
state2 = {}
state3 = {}
state4 = {}
today = datetime.datetime.today().weekday()

def save(path, text):
    with open(path,"w",encoding="utf-8") as file:
        json.dump(text,file, sort_keys=False,indent=4,ensure_ascii=False)

def load(path):
    with open(path, "r",encoding="utf-8") as file:
        result = json.load(file)
    return result

week = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресение"
}
# Command bot
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Command is bot: \n/schedule Для того чтобы увидеть рассписание на сегодня и на завтра, \n /create_note для создание заметки нужно следовать такой конструкции 'название@заметка',\n /list_list Показывает все note в виде списка в котором можно выбрать заметку для отображени.\n edit_note После написание команды нужно написать 'название@измененная заметка'\n /delete_note для удаление заметки вам нужно после ввода команды написать название заметки \n watch_note после ввода нужно написать название заметки")

@bot.message_handler(commands=['create_note'])
def create_note(message): 
    bot.send_message(message.chat.id, "Напишите название и укажите '@' в конце названия новой заметки. После знака собаки все написанное будет записанно в заметку это должно выглядеть так:\n 'Название@Заметка.'")
    state[message.chat.id] = True

@bot.message_handler(func=lambda message: state.get(message.chat.id, False)) # Эта функция нужна для создания заметок. Учитывайте что он записывает словарь!
def create_handler(message):
    if "@" in message.text:
        name, text = message.text.split("@")
        notes = load(path_notes)
        notes[name] = text
        save(path_notes,notes)
        bot.send_message(message.chat.id, f"Заметка '{name}' сохранена")
        state[message.chat.id] = False
    else:
        bot.send_message(message.chat.id, 'Название заметки должно заканчиваться на "@" иначе произойдет неправильное сохранение.')

@bot.message_handler(commands=['edit_note'])
def edit_note(message):
    bot.send_message(message.chat.id, "Напишите название заметки. После написание название напишите @ после которого можно написать новое содержание заметки.")
    state2[message.chat.id] = True
        
@bot.message_handler(func=lambda message: state2.get(message.chat.id, False)) # Эта функция нужна для создания заметок. Учитывайте что он записывает словарь!
def edite_handler(message):
    if "@" in message.text:
        name, text = message.text.split('@')
        notes = load(path_notes)
        if name in notes.keys():
            notes[name] = text
            save(path_notes,notes)
            bot.send_message(message.chat.id, "Изменения сохранены")
            state2[message.chat.id] = False
        else:
            message.send_message(message.chat.id, 'Вы не правильно написали название заметки')
            state2[message.chat.id] = False
    else:
         bot.send_message(message.chat.id, "Вы не правильно написали изменения заметки. Вид который нужен для изменения заметок 'Название@Новое содержание заметки'.")
         state2[message.chat.id] = False

@bot.message_handler(commands=['delete_note'])
def delete_note(message):
    bot.send_message(message.chat.id, "Напишите название заметки для того чтобы удалить заметку.")
    state3[message.chat.id] = True

@bot.message_handler(func=lambda message: state3.get(message.chat.id, False))
def delete_handler(message):
    name = message.text
    notes = load(path_notes)
    if name in notes:
        notes.pop(name)
        bot.send_message(message.chat.id, "Удаление произошло")
        save(path_notes,notes)
        state3[message.chat.id] = False
    else:
        bot.send_message(message.chat.id, "Вы написали неправильно название заметки.")
        state3[message.chat.id] = False

@bot.message_handler(commands=['watch_note'])
def watch_note(message):
    bot.send_message(message.chat.id, "Напишите название заметки для того чтобы увидеть содержание заметки.")
    state4[message.chat.id] = True

@bot.message_handler(func=lambda message: state4.get(message.chat.id, False))
def watch_handler(message):
    name = message.text
    notes = load(path_notes)
    if name in notes:
        bot.send_message(message.chat.id, notes[name])
        state4[message.chat.id] = False
    else:
        bot.send_message(message.chat.id, "Вы написали неправильно название заметки.")
        state4[message.chat.id] = False

@bot.message_handler(commands=['list_note'])
def list_note(message):
    notes = load(path_notes)
    name_list = notes.keys()
    name = ""
    for names in name_list:
        name = name + '\n' + names 
    bot.send_message(message.chat.id, name)
    
@bot.message_handler(commands=['schedule'])
def schedule(message):
    schedule = load(path_schedule)
    parity = schedule[2]
    schedule_output = "Расписание на сегодня\n\n"
    week_parity = 0 if parity else 1
    if week[today] not in ["Суббота","Воскресение"]:
        for lesson in schedule[week_parity][week[today]]:
            schedule_output = schedule_output + " {lesson} | {teacher} | {cabinet} \n".format(lesson=lesson[0],teacher=lesson[2],cabinet=lesson[1])
        if week[today] == "Пятница":
            schedule_output += "\n Расписание на понедельник\n\n"
            for lesson in schedule[not week_parity][week[0]]:
                schedule_output = schedule_output + " {lesson} | {teacher} | {cabinet} \n".format(lesson=lesson[0],teacher=lesson[2],cabinet=lesson[1])
        else:
            schedule_output += "\n Расписание на завтра\n\n"
            for lesson in schedule[week_parity][week[today+1]]:
                schedule_output = schedule_output + " {lesson} | {teacher} | {cabinet} \n".format(lesson=lesson[0],teacher=lesson[2],cabinet=lesson[1])
    else:
        schedule_output += "\n Расписание на понедельник\n\n"
        for lesson in schedule[not week_parity][week[0]]:
            schedule_output = schedule_output + " {lesson} | {teacher} | {cabinet} \n".format(lesson=lesson[0],teacher=lesson[2],cabinet=lesson[1])
    
    bot.send_message(message.chat.id, schedule_output)

@bot.message_handler(commands=['change_week_parity'])
def lol(message):
    schedule = load(path_schedule)
    if schedule[2] == 0:
        schedule[2] = 1
    else:
        schedule[2] = 0
    save(path_schedule, schedule)
    bot.send_message(message.chat.id, 'parity complite')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton("help", callback_data="help")
    button2 = types.InlineKeyboardButton("creat note",callback_data='create_note')
    button3 = types.InlineKeyboardButton("edit note",callback_data='edit_note')
    button4 = types.InlineKeyboardButton("delete note",callback_data="delete_note")
    button5 = types.InlineKeyboardButton("list note",callback_data='list_note')
    button6 = types.InlineKeyboardButton("schedule",callback_data='schedule')
    button7 = types.InlineKeyboardButton("watch note",callback_data='watch_note')
    button8 = types.InlineKeyboardButton("switch week parity", callback_data="change_week_parity")
    markup.add(button1,button2,button3,button4,button5,button6,button7,button8)
    bot.send_message(message.chat.id, 'Привет, этот бот был создан для просмотра расписания и создание заметок. (Примечание заметки не имеют возможности хранить фото)', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    calls = call.message
    if call.data == 'help':
        help_command(calls) 
    elif call.data == 'create_note':
        create_note(call.message) 
    elif call.data == 'edit_note':
        edit_note(call.message) 
    elif call.data == 'delete_note':
        delete_note(call.message) 
    elif call.data == 'list_note':
        list_note(call.message) 
    elif call.data == 'schedule':
        schedule(call.message)
    elif call.data == 'watch_note':
        watch_note(call.message) 
    elif call.data == 'change_week_parity':
        lol(call.message)
bot.infinity_polling()
