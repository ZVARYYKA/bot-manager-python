from manager_token import GetManagerToken
import telebot
import sqlite3
from telebot import types

bot_token = GetManagerToken()
bot = telebot.TeleBot(bot_token)

conn = sqlite3.connect('bot_manager_database.db')

users_dict = dict()
admin_dict = dict()


@bot.message_handler(commands=['myid'])
def get_user_id(message):
    # Отправляем пользователю его user_id
    bot.send_message(message.chat.id, f"Ваш user_id: {message.chat.id}")
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


@bot.callback_query_handler(func=lambda call: call.data in ['start_button', 'to_start_callback_handler_button'])
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

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    
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


# @bot.callback_query_handler(func=lambda call: call.data.startswith('arrrrartist_'))
# def artist_callback_handler(call):
#     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
#     artist_name = call.data.split('_')[1]
#     bot.send_message(call.message.chat.id, f"Вы выбрали артиста: {artist_name}. Напишите ваше сообщение.")
#     bot.register_next_step_handler(call.message, handle_user_message, artist_name)

@bot.callback_query_handler(func=lambda call: call.data.startswith('arrrrartist_'))
def artist_callback_handler(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    artist_name = call.data.split('_')[1]
    bot.send_message(call.message.chat.id, f"Вы выбрали артиста: {artist_name}. Напишите ваш номер телефона.")
    bot.register_next_step_handler(call.message, handle_phone_user_message, artist_name)

def handle_phone_user_message(message, artist_name):
    phone_number = message.text
    if phone_number.isdigit():
        bot.send_message(message.chat.id, "Ваш номер телефона услышан. Напишите ваше ФИО.")
        bot.register_next_step_handler(message, handle_name_user_message, artist_name, phone_number)
        
        
    pass

def handle_name_user_message(message, artist_name, phone_number):
    name = message.text
    bot.send_message(message.chat.id, "Ваше ФИО услышано. Напишите ваше сообщение.")
    bot.register_next_step_handler(message, handle_users_message, artist_name, phone_number, name)
    pass



    
    





# def handle_pers_message(message, artist_name, phone_number,name):
#     message_for_artist = message.text
#    #Обработка персональных данных

#     markup4 = types.InlineKeyboardMarkup()
#     #Добавляем новую кнопку с другим callback_data
#     removed_button = types.InlineKeyboardButton('Начнем', callback_data='removed_button')
#     markup4.add(removed_button)
#     bot.send_message(message.chat.id, "Нажимая кнопку 'Начнем', вы соглашаетесь на обработку персональных данных", reply_markup=markup4)
#     bot.register_next_step_handler(message, handle_users_message, artist_name, phone_number,name,message_for_artist)

def handle_users_message(message, artist_name, phone_number,name):
    # Отправляем сообщение артисту
    
    user = message.from_user.username
    send_message_to_artist(artist_name, message.text, phone_number, user,name)
    bot.send_message(message.chat.id, "Ваше сообщение отправлено артисту. Вскоре вы получите ответ.")
    # # Отправляем сообщение артисту
    # send_message_to_artist(artist_name, message.text)

def send_message_to_artist(artist_name, message_text, phone_number, user,name):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('bot_manager_database.db')

    # Получаем курсор для выполнения SQL-запросов
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM artists WHERE artist_name = '{artist_name}'")
    artist = cursor.fetchone()

    # Отправляем сообщение артисту с информацией о username клиента и его сообщением b его номером телефона
    bot.send_message(artist[2], f"Сообщение от @{user}:\n{message_text}\nНомер телефона: {phone_number} \nФИО: {name}")
    
    
    #Кнопки для выбора, отвечать или нет
    # markup4 = types.InlineKeyboardMarkup()
    # yes_button = types.InlineKeyboardButton('Да', callback_data='yes_button')
    # no_button = types.InlineKeyboardButton('Нет', callback_data='no_button')
    # markup4.add(yes_button, no_button)
    # bot.send_message(artist[2], "Ответить на сообщение?", reply_markup=markup4)


    

    # Закрываем соединение с базой данных
    conn.close()

# @bot.callback_query_handler(func=lambda call: call.data == 'yes_button')
# def yes_callback_handler(call):
#     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
#     bot.send_message(call.message.chat.id, "Ответ отправлен клиенту")
#     # bot.send_message(call.message.chat.id, "Ответ отправлен клиенту")

# @bot.callback_query_handler(func=lambda call: call.data == 'no_button')
# def no_callback_handler(call):
#     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
#     bot.send_message(call.message.chat.id, "Ответ не отправлен клиенту")
#     # bot.send_message(call.message.chat.id, "Ответ не отправлен клиенту")

    
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


@bot.callback_query_handler(func=lambda call: call.data in ['artist_button', 'to_artist_name_callback_handler_button'])
def artist_name_callback_handler(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

    markup_artist1 = types.InlineKeyboardMarkup() 

    to_start_callback_handler_button = types.InlineKeyboardButton('Назад', callback_data='to_start_callback_handler_button')

    markup_artist1.add(to_start_callback_handler_button)
    bot.send_message(call.message.chat.id, "Введите ваше имя/никнейм. С его помощью клиенты смогут обратиться к вам", reply_markup=markup_artist1)


    bot.register_next_step_handler(call.message, handle_artist_name)    


@bot.callback_query_handler(func=lambda call: call.data == 'to_start_callback_handler_button')
def artist_back_callback_handler(call):
    start_callback_handler(call)

def handle_artist_name(message):

    markup_artist2 = types.InlineKeyboardMarkup() 
    
    to_artist_circle_callback_handler_button = types.InlineKeyboardButton('Все верно', callback_data='to_artist_circle_callback_handler_button')
    to_artist_name_callback_handler_button = types.InlineKeyboardButton('Ввести еще раз', callback_data='to_artist_name_callback_handler_button')
    markup_artist2.add(to_artist_circle_callback_handler_button, to_artist_name_callback_handler_button)

    artist_name = message.text

    conn = sqlite3.connect('bot_manager_database.db')

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM artists WHERE artist_name = '{artist_name}'")
    record = cursor.fetchone()



    if record is not None:
        markup_artist3 = types.InlineKeyboardMarkup() 
    
        to_artist_name_callback_handler_button = types.InlineKeyboardButton('Ввести еще раз', callback_data='to_artist_name_callback_handler_button')
        markup_artist3.add(to_artist_name_callback_handler_button)

        bot.send_message(message.chat.id, f'''Артист с именем {artist_name} уже зарегистрирован. 
Помните, что при попытке выдать себя за другого человека  Вы будете заблокированы навсегда''', reply_markup=markup_artist3)
    else:
        users_dict[message.chat.id] = artist_name
        bot.send_message(message.chat.id, f"Ваше имя {artist_name}, не так ли?", reply_markup=markup_artist2)
    conn.close()

    
    
@bot.callback_query_handler(func=lambda call: call.data == 'to_artist_circle_callback_handler_button')
def artist_circle_callback_handler(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, f'''Для подтверждения вашей личности вам необходимо записать видеосообщение с вашим лицом и фразой: 
"Я - {users_dict[call.message.chat.id]}, хочу подтвердить регистрацию для ManagerBot". 
После успешной проверки мы уведомим вас об успешной регистрации.''')
    bot.register_next_step_handler(call.message, artist_handle_video)  
    

@bot.message_handler(content_types=['video_note'])
def artist_handle_video(message):
    
    markup_admin = types.InlineKeyboardMarkup() 
    confirmation_button = types.InlineKeyboardButton('Подтвердить', callback_data=f'confirmation_button {message.chat.id} {users_dict[message.chat.id]}')
    again_button = types.InlineKeyboardButton('Повторный запрос', callback_data=f'again_button {message.chat.id} {users_dict[message.chat.id]}')
    block_button = types.InlineKeyboardButton('Заблокировать', callback_data='block_button')
    markup_admin.add(confirmation_button, again_button, block_button)

    conn = sqlite3.connect('bot_manager_database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT admin_id FROM admins")
    result = cursor.fetchall()

    admins_id = []
    for row in result:
        admins_id.append(row[0])
    for i in range(0, len(admins_id)):
        message1_id = bot.send_video_note(admins_id[i], message.video_note.file_id)
        message2_id = bot.send_message(admins_id[i], f'''Имя: {users_dict[message.chat.id]}
Username: @{message.chat.username} 
User id: {message.chat.id}''', reply_markup=markup_admin)
        admin_dict[admins_id[i]] = [message1_id.message_id, message2_id.message_id, message.chat.id]
    for key, value in admin_dict.items():
        print(key, value)



@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'confirmation_button')
def admin_confirmation_callback_handler(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    artist_id = call.data.split()[1]
    artist_name = call.data.split()[2]
    bot.delete_message

    conn = sqlite3.connect('bot_manager_database.db')
    cursor = conn.cursor()

    #Удаление двух сообщений у других админов
    for key, value in admin_dict.items():
        if str(value[2]) == str(artist_id) and str(key) != str(call.message.chat.id):
            bot.delete_message(chat_id=key, message_id=value[0])
            bot.delete_message(chat_id=key, message_id=value[1])
        
    
    bot.send_message(artist_id, "Регистрация успешно подтверждена. Теперь вам будут приходить коммерческие предложения.")
    cursor.execute('INSERT INTO artists (artist_name, artist_id) VALUES (?, ?)', (artist_name, artist_id))
    conn.commit()

    conn.close()

@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'again_button')
def admin_again_callback_handler(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    artist_id = call.data.split()[1]
    print('artist_id =', artist_id)


    #Удаление двух сообщений у других админов
    for key, value in admin_dict.items():
        if str(value[2]) == str(artist_id) and str(key) != str(call.message.chat.id):
            bot.delete_message(chat_id=key, message_id=value[0])
            bot.delete_message(chat_id=key, message_id=value[1])

    markup_artist4 = types.InlineKeyboardMarkup() 
    again_button = types.InlineKeyboardButton('Попробовать ещё раз', callback_data='to_artist_circle_callback_handler_button')
    markup_artist4.add(again_button)

    bot.send_message(artist_id, "Ваше видеосообщение было рассмотрено, но нам не удалось подтвердить вашу личность. Пожалуйста, попробуйте ещё раз.", reply_markup=markup_artist4)

    
    
    
    
bot.polling(none_stop=True)



