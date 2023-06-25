from manager_token import GetManagerToken
import telebot
import sqlite3
from telebot import types

bot_token = GetManagerToken()
bot = telebot.TeleBot(bot_token)

conn = sqlite3.connect('bot_manager_database.db')

users_dict = dict()
admin_dict = dict()
pers_dict = dict()

ban_string = "На ваш аккаунт наложена блокировка за попытку мошенничества"


def check_ban(message):
    user_id = message.chat.id
    conn = sqlite3.connect('bot_manager_database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM banlist WHERE user_id = '{user_id}'")
    result = cursor.fetchall()
    conn.close()
    return result


@bot.message_handler(commands=['myid'])
def get_user_id(message):
    # Отправляем пользователю его user_id
    bot.send_message(message.chat.id, f"Ваш user_id: {message.chat.id}")


@bot.message_handler(commands=['help'])
def help(message):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        bot.send_message(message.chat.id, "Для начала работы с ботом введите команду /start")


@bot.message_handler(commands=['start'])
def start(message):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        # Создаем панель
        markup1 = types.InlineKeyboardMarkup()
        # Создаем кнопку
        start_button = types.InlineKeyboardButton('Начнем', callback_data='start_button')
        # добавляем кнопку на панель
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


@bot.callback_query_handler(func=lambda call: call.data in ['start_button', 'to_start_callback_handler_button'])
def start_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        # Создаем панель
        markup2 = types.InlineKeyboardMarkup()
        # Создаем кнопку
        client_button = types.InlineKeyboardButton('Клиент', callback_data='client_button')
        artist_button = types.InlineKeyboardButton('Артист', callback_data='artist_button')
        # добавляем кнопку на панель
        markup2.add(client_button, artist_button)

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Как вы хотите использовать бота?", reply_markup=markup2)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)


# ЧАСТЬ ЗВАРЫКИ

@bot.callback_query_handler(func=lambda call: call.data == 'client_button')
def client_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
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
            artist_button = types.InlineKeyboardButton(artist[1],
                                                       callback_data=f"arrrrartist_{artist[1]}")  # Используем имя артиста в качестве callback_data
            markup3.add(artist_button)

        end_button = types.InlineKeyboardButton("Назад", callback_data=f"to_start_callback_handler_button")
        markup3.add(end_button)
        # Отправляем сообщение с панелью кнопок
        bot.send_message(call.message.chat.id, "Выберите артиста", reply_markup=markup3)

        # Закрываем соединение с базой данных
        conn.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('arrrrartist_'))
def artist_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        artist_name = call.data.split('_')[1]
        bot.send_message(call.message.chat.id, f"Вы выбрали артиста: {artist_name}. Напишите ваш номер телефона.")
        bot.register_next_step_handler(call.message, handle_phone_user_message, artist_name)


def handle_phone_user_message(message, artist_name):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        phone_number = message.text
        if phone_number.isdigit():
            bot.send_message(message.chat.id, "Ваш номер телефона услышан. Напишите ваше ФИО.")
            bot.register_next_step_handler(message, handle_name_user_message, artist_name, phone_number)


def handle_name_user_message(message, artist_name, phone_number):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        name = message.text
        bot.send_message(message.chat.id, "Ваше ФИО услышано. Напишите ваше сообщение.")
        bot.register_next_step_handler(message, handle_pers_message, artist_name, phone_number, name)


def handle_pers_message(message, artist_name, phone_number, name):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        # Отправляем сообщение артисту

        user = message.from_user.username
        # Добавляем все значения в словарь pers_dict
        global pers_dict

        pers_dict = {f'name_{user}': name, 'phone_number': phone_number, 'user': user, 'message': message.text,
                     'artist_name': artist_name}

        # Спрашивем разрешеение на обработку персональных данных
        markup4 = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton('✅', callback_data='pers_yes_button')
        no_button = types.InlineKeyboardButton('❌', callback_data='pers_no_button')
        markup4.add(yes_button, no_button)
        bot.send_message(message.chat.id, "Вы согласны на обработку персональных данных?", reply_markup=markup4)


@bot.callback_query_handler(func=lambda call: call.data.startswith('pers_no_button'))
def pers_no_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Вы отказались от обработки персональных данных. Приходите еще.")
        # Очистка словаря
        pers_dict.clear()


@bot.callback_query_handler(func=lambda call: call.data.startswith('pers_yes_button'))
def pers_yes_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        artist_name = pers_dict['artist_name']
        message_user = pers_dict['message']
        phone_number_user = pers_dict['phone_number']
        user = pers_dict['user']
        name = pers_dict[f'name_{user}']
        send_message_to_artist(artist_name, message_user, phone_number_user, user, name)

        # Очистка словаря
        pers_dict.clear()
        bot.send_message(call.message.chat.id, "Ваше сообщение отправлено артисту. Вскоре вы получите ответ.")


def send_message_to_artist(artist_name, message_text, phone_number, user, name):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('bot_manager_database.db')

    # Получаем курсор для выполнения SQL-запросов
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM artists WHERE artist_name = '{artist_name}'")
    artist = cursor.fetchone()

    # Отправляем сообщение артисту с информацией о username клиента и его сообщением b его номером телефона
    bot.send_message(artist[2], f"Сообщение от @{user}:\n{message_text}\nНомер телефона: {phone_number} \nФИО: {name}")
    # Закрываем соединение с базой данных
    conn.close()


# ЧАСТЬ МАКСИМУЛ ПРЕЙНА


@bot.callback_query_handler(func=lambda call: call.data in ['artist_button', 'to_artist_name_callback_handler_button'])
def artist_name_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

        markup_artist1 = types.InlineKeyboardMarkup()

        to_start_callback_handler_button = types.InlineKeyboardButton('Назад',
                                                                      callback_data='to_start_callback_handler_button')

        markup_artist1.add(to_start_callback_handler_button)

        bot.send_message(call.message.chat.id,
                         "Введите ваше имя/никнейм. С его помощью клиенты смогут обратиться к вам",
                         reply_markup=markup_artist1)

        bot.register_next_step_handler(call.message, handle_artist_name)


@bot.callback_query_handler(func=lambda call: call.data == 'to_start_callback_handler_button')
def artist_back_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        start_callback_handler(call)


def handle_artist_name(message):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        markup_artist2 = types.InlineKeyboardMarkup()
        to_artist_circle_callback_handler_button = types.InlineKeyboardButton('Все верно',
                                                                              callback_data='to_artist_circle_callback_handler_button')
        to_artist_name_callback_handler_button = types.InlineKeyboardButton('Ввести еще раз',
                                                                            callback_data='to_artist_name_callback_handler_button')
        markup_artist2.add(to_artist_circle_callback_handler_button, to_artist_name_callback_handler_button)

        artist_name = message.text

        conn = sqlite3.connect('bot_manager_database.db')

        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM artists WHERE artist_name = '{artist_name}'")
        record = cursor.fetchone()

    if record is not None:
        markup_artist3 = types.InlineKeyboardMarkup()
        to_artist_name_callback_handler_button = types.InlineKeyboardButton('Ввести еще раз',
                                                                            callback_data='to_artist_name_callback_handler_button')
        markup_artist3.add(to_artist_name_callback_handler_button)

        bot.send_message(message.chat.id, f'''Артист с именем {artist_name} уже зарегистрирован. 
Помните, что при попытке выдать себя за другого человека  Вы будете заблокированы навсегда''',
                         reply_markup=markup_artist3)
    else:
        users_dict[message.chat.id] = artist_name
        bot.send_message(message.chat.id, f"Ваше имя {artist_name}, не так ли?", reply_markup=markup_artist2)
    conn.close()


@bot.callback_query_handler(func=lambda call: call.data == 'to_artist_circle_callback_handler_button')
def artist_circle_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, f'''Для подтверждения вашей личности вам необходимо записать видеосообщение с вашим лицом и фразой: 
"Я - {users_dict[call.message.chat.id]}, хочу подтвердить регистрацию для ManagerBot". 
После успешной проверки мы уведомим вас об успешной регистрации.''')
        bot.register_next_step_handler(call.message, artist_handle_video)


@bot.message_handler(content_types=['video_note'])
def artist_handle_video(message):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        markup_admin = types.InlineKeyboardMarkup()
        confirmation_button = types.InlineKeyboardButton('Подтвердить',
                                                         callback_data=f'confirmation_button {message.chat.id} {users_dict[message.chat.id]}')
        again_button = types.InlineKeyboardButton('Повторный запрос',
                                                  callback_data=f'again_button {message.chat.id} {users_dict[message.chat.id]}')
        block_button = types.InlineKeyboardButton('Заблокировать',
                                                  callback_data=f'block_button {message.chat.id} {message.from_user.username}')
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
    # for key, value in admin_dict.items():
    #     print(key, value)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'confirmation_button')
def admin_confirmation_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        artist_id = call.data.split()[1]
        artist_name = call.data.split()[2]
        bot.delete_message

        conn = sqlite3.connect('bot_manager_database.db')
        cursor = conn.cursor()

        # Удаление двух сообщений у других админов
        for key, value in admin_dict.items():
            if str(value[2]) == str(artist_id) and str(key) != str(call.message.chat.id):
                bot.delete_message(chat_id=key, message_id=value[0])
                bot.delete_message(chat_id=key, message_id=value[1])

        bot.send_message(artist_id,
                         "Регистрация успешно подтверждена. Теперь вам будут приходить коммерческие предложения.")
        cursor.execute('INSERT INTO artists (artist_name, artist_id) VALUES (?, ?)', (artist_name, artist_id))
        conn.commit()

        conn.close()


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'again_button')
def admin_again_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        artist_id = call.data.split()[1]

        # Удаление двух сообщений у других админов
        for key, value in admin_dict.items():
            if str(value[2]) == str(artist_id) and str(key) != str(call.message.chat.id):
                bot.delete_message(chat_id=key, message_id=value[0])
                bot.delete_message(chat_id=key, message_id=value[1])

        markup_artist4 = types.InlineKeyboardMarkup()
        again_button = types.InlineKeyboardButton('Попробовать ещё раз',
                                                  callback_data='to_artist_circle_callback_handler_button')
        markup_artist4.add(again_button)

        bot.send_message(artist_id,
                         "Ваше видеосообщение было рассмотрено, но нам не удалось подтвердить вашу личность. Пожалуйста, попробуйте ещё раз.",
                         reply_markup=markup_artist4)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'block_button')
def admin_block_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        artist_id = call.data.split()[1]
        user_name = call.data.split()[2]

        conn = sqlite3.connect('bot_manager_database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO banlist (user_name, user_id) VALUES (?, ?)', (user_name, artist_id))
        conn.commit()
        conn.close()
        # Удаление двух сообщений у других админов
        for key, value in admin_dict.items():
            if str(value[2]) == str(artist_id) and str(key) != str(call.message.chat.id):
                bot.delete_message(chat_id=key, message_id=value[0])
                bot.delete_message(chat_id=key, message_id=value[1])
        bot.send_message(call.message.chat.id, "Пользователь заблокирован")
        bot.send_message(artist_id,
                         "Ваше видеосообщение было рассмотрено. Вы были заблокированы за попытку мошенничества.")


@bot.message_handler(commands=['unblock'])
def unblock(message):
    user_id = message.chat.id

    conn = sqlite3.connect('bot_manager_database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT admin_id FROM admins")
    result = cursor.fetchall()

    admins_id = []
    for row in result:
        admins_id.append(row[0])

    conn.close()

    markup_admin_unblock = types.InlineKeyboardMarkup()
    unblock_user_id_buttton = types.InlineKeyboardButton('Ввести ID', callback_data='to_unblock_user_id_buttton')
    unblock_user_name_button = types.InlineKeyboardButton('Ввести username',
                                                          callback_data='to_unblock_user_name_button')
    markup_admin_unblock.add(unblock_user_id_buttton, unblock_user_name_button)

    if str(user_id) in admins_id:
        bot.send_message(message.chat.id, "Выберите", reply_markup=markup_admin_unblock)


@bot.callback_query_handler(func=lambda call: call.data == 'to_unblock_user_id_buttton')
def unblock_user_id(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Введите ID пользователя")
    bot.register_next_step_handler(call.message, unblock_user_id_input)


@bot.callback_query_handler(func=lambda call: call.data == 'to_unblock_user_name_button')
def unblock_user_name(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Введите имя пользователя")
    bot.register_next_step_handler(call.message, unblock_user_name_input)


@bot.callback_query_handler(func=lambda call: call.data == 'to_back_unblock_button')
def back_unblock(call):
    bot.register_next_step_handler(call.message, unblock)


def unblock_user_id_input(message):
    user_id = message.text
    conn = sqlite3.connect('bot_manager_database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM banlist WHERE user_id = '{user_id}'")
    result = cursor.fetchall()
    if result:
        user_id = result[0][2]
        cursor.execute(f"DELETE FROM banlist WHERE user_id = '{user_id}'")
        conn.commit()
        bot.send_message(message.chat.id, f"Пользователь с ID {user_id} разблокирован")
    else:
        bot.send_message(message.chat.id, "Данный пользователь не заблокирован")

    conn.close()


def unblock_user_name_input(message):
    user_name = message.text
    conn = sqlite3.connect('bot_manager_database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM banlist WHERE user_name = '{user_name}'")
    result = cursor.fetchall()
    if result:
        user_id = result[0][2]
        cursor.execute(f"DELETE FROM banlist WHERE user_id = '{user_id}'")
        conn.commit()
        bot.send_message(message.chat.id, f"Пользователь с именем {user_name} разблокирован")
    else:
        bot.send_message(message.chat.id, "Данный пользователь не заблокирован")

    conn.close()


bot.polling(none_stop=True)
