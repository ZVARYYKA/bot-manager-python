from manager_token import GetManagerToken
import telebot
import sqlite3
from telebot import types

bot_token = GetManagerToken()
bot = telebot.TeleBot(bot_token)

conn = sqlite3.connect('bot_manager_database.db')

@bot.message_handler(commands=['start'])
def start(message):

    #Создаем панель
    markup1 = types.InlineKeyboardMarkup() 
    #Создаем кнопку
    start_button = types.InlineKeyboardButton('Начнем', callback_data='start_button')
    #добавляем кнопку на панель
    markup1.add(start_button)

    bot.send_message(message.chat.id, 
                     '''Вас приветствует StarManager Бот - ваш верный помощник в сфере музыкального менеджмента и продвижения вашей музыки.\n
Мы предлагаем широкий спектр услуг, чтобы помочь вам достичь успеха в индустрии музыки. 
Наш бот способен выполнять функции менеджера для артистов/певцов. \n
С помощью StarManager, вы можете получить предложения по музыке и оптимальные условия для сотрудничества. 
Мы также предоставляем возможность рекламы в социальных сетях, где миллионы пользователей смогут оценить ваше творчество.\n
Вы сможете получить обратную связь от своей аудитории и следить 
за развитием своей карьеры с помощью многочисленных отчетов о продвижении и продажах.\n
Наш бот обеспечивает полный спектр услуг для успешной карьеры в музыке. 
Не ждите больше, начинайте работать с нами и достигните музыкального успеха!''',
    reply_markup=markup1)

# #хз зачем это
    # markup1 = types.InlineKeyboardMarkup()
    # #Добавляем новую кнопку с другим callback_data
    # removed_button = types.InlineKeyboardButton('Начнем', callback_data='removed_button')
    # #Добавляем кнопку на markup
    # markup1.row(removed_button)

# @bot.callback_query_handler(func=lambda call: call.data == 'start_button')
# def lets_start(call):
#     bot.send_message(call.message.chat.id, "Всё заебись")


@bot.callback_query_handler(func=lambda call: call.data == 'start_button')
def start_callback_handler(call):
    #Создаем панель
    markup2 = types.InlineKeyboardMarkup() 
    #Создаем кнопку
    client_button = types.InlineKeyboardButton('Клиент', callback_data='client_button')
    artist_button = types.InlineKeyboardButton('Артист', callback_data='artist_button')
    #добавляем кнопку на панель
    markup2.add(client_button, artist_button)
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Как вы хотите использовать бота?", reply_markup=markup2)
    
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    

#ЧАСТЬ ЗВАРЫКИ

@bot.callback_query_handler(func=lambda call: call.data == 'client_button')
def client_callback_handler(call):
    bot.answer_callback_query(call.id)

    # Создаем соединение с базой данных
    conn = sqlite3.connect('bot_manager_database.db')

    # Получаем курсор для выполнения SQL-запросов
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM artists")
    artists = cursor.fetchall()

    # Создаем панель
    markup3 = types.InlineKeyboardMarkup()

    # Создаем кнопку для каждого артиста
    for artist in artists:
        artist_button = types.InlineKeyboardButton(artist[1], callback_data=f"arrrrartist_{artist[1]}")  # Используем имя артиста в качестве callback_data
        markup3.add(artist_button)

    # Отправляем сообщение с панелью кнопок
    bot.send_message(call.message.chat.id, "Выберите артиста", reply_markup=markup3)

    # Закрываем соединение с базой данных
    conn.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('arrrrartist_'))
def artist_callback_handler(call):
    artist_name = call.data.split('_')[1]
    bot.send_message(call.message.chat.id, f"Вы выбрали артиста: {artist_name}. Напишите ваше сообщение.")

    
# @bot.callback_query_handler(func=lambda call: True) 
# def artist_callback_handler(call):
#     if call.data.startswith('artist_'):
#         artist_name = call.data.split('_')[1]  # Получаем имя артиста из callback_data
#         bot.send_message(call.message.chat.id, f"Выбран артист: {artist_name}")

# НЕ УДАЛЯТЬ
# @bot.message_handler(func=lambda message: True)
# def handle_message(message):
#     user_id = message.chat.id

#     # Вместо этого используйте свою логику для получения user_id из таблицы
#     # user_id = ...

#     # Отправляем сообщение пользователю от имени бота
#     bot.send_message(user_id, "Сообщение получено. Спасибо!")  



#ЧАСТЬ МАКСИМУЛ ПРЕЙНА


@bot.callback_query_handler(func=lambda call: call.data == 'artist_button')
def artist_callback_handler(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    #Создаем панель
    markup_artist1 = types.InlineKeyboardMarkup() 
    #Создаем кнопку
    back_button = types.InlineKeyboardButton('Назад', callback_data='back_button')
    #добавляем кнопку на панель
    markup_artist1.add(back_button)
    bot.send_message(call.message.chat.id, "Введите ваше имя/никнейм. С его помощью клиенты смогут обратиться к вам", reply_markup=markup_artist1)
    bot.register_next_step_handler(call.message, handle_artist_name)

@bot.callback_query_handler(func=lambda call: call.data == 'back_button')
def artist_callback_handler(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    start_callback_handler(call)

def handle_artist_name(message):
    artist_name = message.text
    bot.send_message(message.chat.id, f"Ваше имя {artist_name}, не так ли?")


    #bot.register_next_step_handler(message, handle_artist_description)

# @bot.message_handler(content_type=['text'])
# def artist_name_handler(message):
#     last_message = bot.get_message_handler(message.chat.id).last_message
    
#     print(last_message)
#     artist_name = message.text




# def handle_name(message):
#     # Сохраняем имя в переменную или базу данных
#     artist_name = message.text
#     # Отправляем сообщение с просьбой ввести контактные данные
#     bot.send_message(message.chat.id, f"Отлично, {artist_name}! Теперь введите свои контактные данные")
#     # Регистрируем обработчик для сообщения с контактными данными
#     #bot.register_next_step_handler(message, handle_contacts, name)

bot.polling(none_stop=True)



