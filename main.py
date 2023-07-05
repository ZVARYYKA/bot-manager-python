from manager_token import GetManagerToken
import telebot
import sqlite3
from telebot import types
from channel_id import GetChannelId

bot_token = GetManagerToken()
bot = telebot.TeleBot(bot_token)

conn = sqlite3.connect('bot_manager_database.db')

users_dict = dict()
admin_dict = dict()
artist_confirmation = dict()
message_and_admin_dict = dict()

pers_dict = dict()


ban_string = "Your account has been banned"


def check_ban(message):
    user_id = message.chat.id
    conn = sqlite3.connect('bot_manager_database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM banlist WHERE user_id = '{user_id}'")
    result = cursor.fetchall()
    conn.close()
    return result


def wrong_data(message):
    if check_user_language(message) == [('ru',)]:
        bot.send_message(message.chat.id, "❌ Вы ввели неверные данные, попробуйте снова")
    elif check_user_language(message) == [('en',)]:
        bot.send_message(message.chat.id, "❌ You entered the wrong data, try again")

@bot.message_handler(commands=['help'])
def help(message):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        if check_user_language(message) == [('ru',)]:
            bot.send_message(message.chat.id, '''▶ Для начала работы с ботом введите /start
🌏Для смены языка введите /language''')
            
        elif check_user_language(message) == [('en',)]:
            bot.send_message(message.chat.id, '''▶ To start working with the bot, type /start
🌏To change the language type /language''')


# Выбор языка для использоапния бота, инфоормация о выборе заноситься в базу данных
@bot.message_handler(commands=['language'])
def language(message):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        markup = types.InlineKeyboardMarkup()
        ru_button = types.InlineKeyboardButton('🇷🇺 Русский', callback_data='ru_button')
        en_button = types.InlineKeyboardButton('🇬🇧 English', callback_data='en_button')
        markup.add(ru_button, en_button)
        bot.send_message(message.chat.id, "Выберите язык \nChoose language ⤵", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['ru_button', 'en_button'])
def language_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        conn = sqlite3.connect('bot_manager_database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM language WHERE user_id = '{call.message.chat.id}'")
        existing_language = cursor.fetchone()
        if call.data == 'ru_button':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "✔️ Вы выбрали русский язык")
            if existing_language:
                # Если запись уже существует, обновляем значение language
                cursor.execute(f"UPDATE language SET language = 'ru' WHERE user_id = '{call.message.chat.id}'")
            else:
                # Иначе, добавляем новую запись
                cursor.execute(f"INSERT INTO language (user_id, language) VALUES ('{call.message.chat.id}', 'ru')")
            
            conn.commit()
            conn.close()
        elif call.data == 'en_button':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "✔️ You have chosen English ")

            if existing_language:
                # Если запись уже существует, обновляем значение language
                cursor.execute(f"UPDATE language SET language = 'en' WHERE user_id = '{call.message.chat.id}'")
            else:
                # Иначе, добавляем новую запись
                cursor.execute(f"INSERT INTO language (user_id, language) VALUES ('{call.message.chat.id}', 'en')")

            conn.commit()
            conn.close()

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        user_language = check_user_language(call.message)
        # Language is already set, proceed with the main functionality
        handle_start_with_language(call.message, user_language[0][0])

# Проверка на наличие пользователя в базе данных
def check_user_language(message, artist_id = None):
    if artist_id == None:
        user_id = message.chat.id
    else:
        user_id = artist_id
    conn = sqlite3.connect('bot_manager_database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT language FROM language WHERE user_id = '{user_id}'")
    result = cursor.fetchall()
    conn.close()
    return result


@bot.message_handler(commands=['start'])
def start(message):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        user_language = check_user_language(message)
        if user_language:
            # Language is already set, proceed with the main functionality
            handle_start_with_language(message, user_language[0][0])
        else:
            # Language is not set, ask the user to choose a language
            language(message)


def handle_start_with_language(message, language):
    if language == 'ru':
        markup1 = types.InlineKeyboardMarkup()
        start_button = types.InlineKeyboardButton('Начнем', callback_data='start_button')
        markup1.add(start_button)
        bot.send_message(message.chat.id, '''Вас приветствует ⭐ StarManager - ваш верный помощник в сфере музыкального менеджмента и продвижения вашей музыки 📈\n
С помощью бота, вы можете получить предложения по музыке и выбрать оптимальные условия для сотрудничества 📨''',
                         reply_markup=markup1)
    elif language == 'en':
        markup1 = types.InlineKeyboardMarkup()
        start_button = types.InlineKeyboardButton('Let\'s start', callback_data='start_button')
        markup1.add(start_button)
        bot.send_message(message.chat.id, '''Welcome to ⭐ StarManager - your faithful assistant in the field of music management and promotion of your music 📈\n
With the help of the bot, you can get music offers and choose the best conditions for cooperation 📨''',
                         reply_markup=markup1)


@bot.callback_query_handler(func=lambda call: call.data in ['start_button', 'to_start_callback_handler_button'])
def start_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        # Создаем панель
        markup2 = types.InlineKeyboardMarkup()
        # Создаем кнопку
        if check_user_language(call.message) == [('ru',)]:
            client_button = types.InlineKeyboardButton('💼 Клиент', callback_data='client_button')
            artist_button = types.InlineKeyboardButton('🎵 Артист', callback_data='artist_button')
            markup2.add(client_button, artist_button)
            bot.send_message(call.message.chat.id, "Как вы хотите использовать бота ❔", reply_markup=markup2)
        elif check_user_language(call.message) == [('en',)]:
            client_button = types.InlineKeyboardButton('💼 Client', callback_data='client_button')
            artist_button = types.InlineKeyboardButton('🎵 Artist', callback_data='artist_button')
            markup2.add(client_button, artist_button)
            bot.send_message(call.message.chat.id, "How you want use bot ❔", reply_markup=markup2)
        # добавляем кнопку на панель

        bot.answer_callback_query(call.id)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)


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

    # Отправляем сообщение с панелью кнопок
    if check_user_language(call.message) == [('ru',)]:
        end_button = types.InlineKeyboardButton("⬅ Назад", callback_data=f"to_start_callback_handler_button")
        markup3.add(end_button)
        bot.send_message(call.message.chat.id, "🎶 Выберите артиста", reply_markup=markup3)

    elif check_user_language(call.message) == [('en',)]:
        end_button = types.InlineKeyboardButton("⬅ Back", callback_data=f"to_start_callback_handler_button")
        markup3.add(end_button)
        bot.send_message(call.message.chat.id, "🎶 Choose an artist", reply_markup=markup3)

        # Закрываем соединение с базой данных
        conn.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('arrrrartist_'))
def artist_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        artist_name = call.data.split('_')[1]
        if check_user_language(call.message) == [('ru',)]:
            bot.send_message(call.message.chat.id, f"Вы выбрали артиста: {artist_name}. Напишите ваш номер телефона 🔢")
        elif check_user_language(call.message) == [('en',)]:
            bot.send_message(call.message.chat.id, f"You choose artist: {artist_name}. Write your phone number 🔢")
        bot.register_next_step_handler(call.message, handle_phone_user_message, artist_name)


def handle_phone_user_message(message, artist_name):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        try:
            if message.text is None or '/' in message.text:
                wrong_data(message)
                bot.register_next_step_handler(message, handle_phone_user_message, artist_name)
            else:
                phone_number = message.text
                if phone_number.isdigit():
                    if check_user_language(message) == [('ru',)]:
                        bot.send_message(message.chat.id, "Отлично. Напишите ваше ФИО 🔠")
                    elif check_user_language(message) == [('en',)]:
                        bot.send_message(message.chat.id, "Great. Write your full name 🔠")
                    bot.register_next_step_handler(message, handle_name_user_message, artist_name, phone_number)
                else:
                    wrong_data(message)
                    bot.register_next_step_handler(message, handle_phone_user_message, artist_name)


        except:
            markup3 = types.InlineKeyboardMarkup()
            end_button = types.InlineKeyboardButton("⬅ Назад", callback_data=f"arrrrartist_")
            markup3.add(end_button)
            wrong_data(message)


def handle_name_user_message(message, artist_name, phone_number):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        try:
            if message.text == None or '/' in message.text:
                wrong_data(message)
                bot.register_next_step_handler(message, handle_name_user_message, artist_name, phone_number)
            else:
                name = message.text
                if check_user_language(message) == [('ru',)]:
                    bot.send_message(message.chat.id, "Великолепно. Напишите ваше сообщение 📝")
                elif check_user_language(message) == [('en',)]:
                    bot.send_message(message.chat.id, "Perfectly. Write your message 📝")
                bot.register_next_step_handler(message, handle_pers_message, artist_name, phone_number, name)
        except:
            wrong_data(message)
            # Перенаправление обратно на функцию handle_name_user_message()
            bot.register_next_step_handler(message, handle_name_user_message, artist_name, phone_number)


def handle_pers_message(message, artist_name, phone_number, name):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        try:
            if message.text is None or '/' in message.text:
                wrong_data(message)
                # Перенаправление обратно на функцию handle_name_user_message()
                bot.register_next_step_handler(message, handle_pers_message, artist_name, phone_number, name)
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
                #no_button = types.InlineKeyboardButton('❌', callback_data='pers_no_button')
                markup4.add(yes_button)
                if check_user_language(message) == [('ru',)]:
                    bot.send_message(message.chat.id, "Вы согласны на обработку персональных данных?",
                                     reply_markup=markup4)
                elif check_user_language(message) == [('en',)]:
                    bot.send_message(message.chat.id, "Do you agree to the processing of personal data?",
                                     reply_markup=markup4)
        except:
           wrong_data(message)
           bot.register_next_step_handler(message, handle_pers_message, artist_name, phone_number, name)

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
        if check_user_language(call.message) == [('ru',)]:
            bot.send_message(call.message.chat.id, "Ваше сообщение отправлено артисту ✅")
        elif check_user_language(call.message) == [('en',)]:
            bot.send_message(call.message.chat.id,
                             "Your message has been sent to the artist ✅")


def send_message_to_artist(artist_name, message_text, phone_number, user, name):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('bot_manager_database.db')

    # Получаем курсор для выполнения SQL-запросов
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM artists WHERE artist_name = '{artist_name}'")
    artist = cursor.fetchone()
     
    artist_id = str(artist[2])

    if check_user_language(None, artist_id) == [('ru',)]:
        # Отправляем сообщение артисту с информацией о username клиента и его сообщением b его номером телефона
        bot.send_message(artist_id, f"📦 Новое сообщение от @{user}:\n{message_text} 📦\n📱 Номер телефона: {phone_number} \n👨‍💻 ФИО: {name}")

    elif check_user_language(None, artist_id) == [('en',)]:
        bot.send_message(artist_id, f"📦 New Message by @{user}:\n{message_text} 📦\n📱 Phone number: {phone_number} \n👨‍💻 Full name: {name}")
    # Закрываем соединение с базой данных
    conn.close()


@bot.callback_query_handler(func=lambda call: call.data in ['artist_button', 'to_artist_name_callback_handler_button'])
def artist_name_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

        markup_artist1 = types.InlineKeyboardMarkup()

        if check_user_language(call.message) == [('ru',)]:
            to_start_callback_handler_button = types.InlineKeyboardButton('⬅ Назад',
                                                                          callback_data='to_start_callback_handler_button')
            markup_artist1.add(to_start_callback_handler_button)
            bot.send_message(call.message.chat.id,
                             "Введите ваше имя/никнейм 🔠\nС его помощью клиенты смогут обратиться к вам 👨‍💻",
                             reply_markup=markup_artist1)
        elif check_user_language(call.message) == [('en',)]:
            to_start_callback_handler_button = types.InlineKeyboardButton('⬅ Back',
                                                                          callback_data='to_start_callback_handler_button')
            markup_artist1.add(to_start_callback_handler_button)
            bot.send_message(call.message.chat.id,
                             "Enter your name / nickname 🔠\nWith its help, clients will be able to contact you 👨‍💻",
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
        if message.text is None or '/' in message.text:
            markup_artist3_1 = types.InlineKeyboardMarkup()
            if check_user_language(message) == [('ru',)]:
                to_artist_name_callback_handler_button = types.InlineKeyboardButton('⬅ Назад',
                                                                                    callback_data='to_artist_name_callback_handler_button')
                markup_artist3_1.add(to_artist_name_callback_handler_button)
                bot.send_message(message.chat.id, "⚠      ошибка      ⚠ \nПопробуйте ещё раз",
                                 reply_markup=markup_artist3_1)
            if check_user_language(message) == [('en',)]:
                to_artist_name_callback_handler_button = types.InlineKeyboardButton('⬅ Back',
                                                                                    callback_data='to_artist_name_callback_handler_button')
                markup_artist3_1.add(to_artist_name_callback_handler_button)
                bot.send_message(message.chat.id, "⚠error⚠ \n Try again", reply_markup=markup_artist3_1)


        else:
            markup_artist2 = types.InlineKeyboardMarkup()
            if check_user_language(message) == [('ru',)]:
                to_artist_circle_callback_handler_button = types.InlineKeyboardButton('Все верно ✅',
                                                                                      callback_data='to_artist_circle_callback_handler_button')
                to_artist_name_callback_handler_button = types.InlineKeyboardButton('Ввести еще раз ❌',
                                                                                    callback_data='to_artist_name_callback_handler_button')
            elif check_user_language(message) == [('en',)]:
                to_artist_circle_callback_handler_button = types.InlineKeyboardButton('All right ✅',
                                                                                      callback_data='to_artist_circle_callback_handler_button')
                to_artist_name_callback_handler_button = types.InlineKeyboardButton('Enter again ❌',
                                                                                    callback_data='to_artist_name_callback_handler_button')
            markup_artist2.add(to_artist_circle_callback_handler_button, to_artist_name_callback_handler_button)

            artist_name = message.text

            conn = sqlite3.connect('bot_manager_database.db')

            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM artists WHERE artist_name = '{artist_name}'")
            record = cursor.fetchone()
            if record is not None:
                markup_artist3_2 = types.InlineKeyboardMarkup()
                if check_user_language(message) == [('ru',)]:
                    to_artist_name_callback_handler_button = types.InlineKeyboardButton('Ввести еще раз',
                                                                                        callback_data='to_artist_name_callback_handler_button')
                    markup_artist3_2.add(to_artist_name_callback_handler_button)
                    bot.send_message(message.chat.id, f'''Артист с именем {artist_name} уже зарегистрирован . 
Помните, что при попытке выдать себя за другого человека Вы будете заблокированы навсегда 🚫''',
                                     reply_markup=markup_artist3_2)
                elif check_user_language(message) == [('en',)]:
                    to_artist_name_callback_handler_button = types.InlineKeyboardButton('Enter again',
                                                                                        callback_data='to_artist_name_callback_handler_button')
                    markup_artist3_2.add(to_artist_name_callback_handler_button)
                    bot.send_message(message.chat.id,
                                     f'''The artist with the name {artist_name} is already registered. Remember that if you try to impersonate another person, you will be blocked forever 🚫''')

            else:
                users_dict[message.chat.id] = artist_name
                if check_user_language(message) == [('ru',)]:
                    bot.send_message(message.chat.id, f"Ваше имя {artist_name}, не так ли ❔",
                                     reply_markup=markup_artist2)
                elif check_user_language(message) == [('en',)]:
                    bot.send_message(message.chat.id, f"Your name is {artist_name}, isn't it ❔",
                                     reply_markup=markup_artist2)
            conn.close()


@bot.callback_query_handler(func=lambda call: call.data == 'to_artist_circle_callback_handler_button')
def artist_circle_callback_handler(call):
    if check_ban(call.message):
        bot.send_message(call.message.chat.id, ban_string)
    else:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if check_user_language(call.message) == [('ru',)]:
            bot.send_message(call.message.chat.id, f'''Для подтверждения вашей личности ☑ вам необходимо записать видеосообщение 🎬 с вашим лицом и фразой:\n
"Я - {users_dict[call.message.chat.id]}, хочу подтвердить регистрацию для StarManagerBot".\n
После успешной проверки мы уведомим вас об успешной регистрации.''')
        elif check_user_language(call.message) == [('en',)]:
            bot.send_message(call.message.chat.id,
                             f'''To confirm your identity ☑, you need to record a video message 🎬 with your face and the phrase:\n
I am {users_dict[call.message.chat.id]}, I want to confirm the registration for StarManagerboot."\n
After successful verification, we will notify you of successful registration.''')

        bot.register_next_step_handler(call.message, artist_handle_video)


def artist_handle_video(message):
    if check_ban(message):
        bot.send_message(message.chat.id, ban_string)
    else:
        try:
            channel_id = GetChannelId()
            response = bot.get_chat_members_count(channel_id)
            total_members = response - 1

            markup_admin = types.InlineKeyboardMarkup()
            confirmation_button = types.InlineKeyboardButton(f'✅ 0/{total_members}',
                                                                callback_data=f'confirmation_button {message.chat.id} {users_dict[message.chat.id]} {message.from_user.username}')
            again_button = types.InlineKeyboardButton(f'🔄 0/{total_members}',
                                                        callback_data=f'again_button {message.chat.id} {users_dict[message.chat.id]} {message.from_user.username}')
            block_button = types.InlineKeyboardButton(f'❌ 0/{total_members}',
                                                        callback_data=f'block_button {message.chat.id} {users_dict[message.chat.id]} {message.from_user.username}')
            markup_admin.add(confirmation_button, again_button, block_button)

            message1 = bot.send_video_note(channel_id, message.video_note.file_id)
            message2 = bot.send_message(channel_id, f'''Имя: {users_dict[message.chat.id]}
Username: @{message.chat.username} 
User id: {message.chat.id}''', reply_markup=markup_admin)

            artist_confirmation[str(message.chat.id)] = [message1, message2]
        except:
            wrong_data(message)


def sollution(total_voted0, total_voted1, total_voted2, artist_id, artist_name, user_name, message1, message2):
    if total_voted0 > (total_voted1 + total_voted2):
        bot.edit_message_reply_markup(chat_id=GetChannelId(), message_id=message2.message_id)
        conn = sqlite3.connect('bot_manager_database.db')
        cursor = conn.cursor()
        if check_user_language(None, artist_id) == [('ru',)]:
            bot.send_message(artist_id,
                            "Регистрация успешно подтверждена✅ Теперь вам будут приходить коммерческие предложения.")
        elif check_user_language(None, artist_id) == [('en',)]:
            bot.send_message(artist_id,
                            "Registration has been successfully confirmed✅ Now you will receive commercial offers.")
        cursor.execute('INSERT INTO artists (artist_name, artist_id) VALUES (?, ?)', (artist_name, artist_id))
        conn.commit()
        bot.send_message(GetChannelId(), "Регистрация подтверждена ✅")
    elif total_voted0 == (total_voted1 + total_voted2) or total_voted2 == (
            total_voted0 + total_voted1) or total_voted1 > (total_voted0 + total_voted2):
        bot.edit_message_reply_markup(chat_id=GetChannelId(), message_id=message2.message_id)
        markup_artist4 = types.InlineKeyboardMarkup()
        again_button = types.InlineKeyboardButton('Попробовать ещё раз 🔄',
                                                  callback_data='to_artist_circle_callback_handler_button')
        markup_artist4.add(again_button)
        bot.send_message(GetChannelId(), "Повторная проверка")
        if check_user_language(None, artist_id) == [('ru',)]:
            bot.send_message(artist_id,
                         "Ваше видеосообщение было рассмотрено, но нам не удалось подтвердить вашу личность 🗿\n Пожалуйста, попробуйте ещё раз 🔄",
                         reply_markup=markup_artist4)
        elif check_user_language(None, artist_id) == [('en',)]:
            bot.send_message(artist_id,
                         "Your video message has been reviewed, but we have not been able to confirm your identity 🗿\n Please try again 🔄",
                         reply_markup=markup_artist4)
        
    elif total_voted2 > (total_voted0 + total_voted1):
        bot.edit_message_reply_markup(chat_id=GetChannelId(), message_id=message2.message_id)
        conn = sqlite3.connect('bot_manager_database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO banlist (user_name, user_id) VALUES (?, ?)', (user_name, artist_id))
        conn.commit()
        conn.close()
        bot.send_message(GetChannelId(), "Пользователь заблокирован 🚫")
        if check_user_language(None, artist_id) == [('ru',)]:
            bot.send_message(artist_id,
                         "Ваше видеосообщение было рассмотрено. Вы были заблокированы за попытку мошенничества 🚫")
        elif check_user_language(None, artist_id) == [('en',)]:
            bot.send_message(artist_id,
                         "Your video message has been reviewed. You have been blocked for attempted fraud 🚫")
    message2_id = message2.message_id
    del message_and_admin_dict[message2_id]


@bot.callback_query_handler(
    func=lambda call: call.data.split()[0] in ['confirmation_button', 'again_button', 'block_button'])
def admin_edit_markup(call):
    admin_id = str(call.from_user.id)

    artist_id = str(call.data.split()[1])
    artist_name = call.data.split()[2]
    user_name = call.data.split()[3]
    message1 = artist_confirmation[artist_id][0]
    message2 = artist_confirmation[artist_id][1]
    message2_id = message2.message_id
    if message2_id not in message_and_admin_dict:
        message_and_admin_dict[message2_id] = []
    if admin_id not in message_and_admin_dict[message2_id]:
        if message2.reply_markup and isinstance(message2.reply_markup, telebot.types.InlineKeyboardMarkup):
            for row in message2.reply_markup.keyboard:
                row_info = []
                for button in row:
                    button_info = {
                        'text': button.text,
                        'callback_data': button.callback_data
                    }
                    row_info.append(button_info)
                keyboard_info = row_info

        dict0 = keyboard_info[0]
        dict1 = keyboard_info[1]
        dict2 = keyboard_info[2]

        total_voted0 = int(dict0['text'].split()[1].split('/')[0])
        total_voted1 = int(dict1['text'].split()[1].split('/')[0])
        total_voted2 = int(dict2['text'].split()[1].split('/')[0])

        total_members = int(dict0['text'].split()[1].split('/')[1])

        callback_data0 = dict0['callback_data']
        callback_data1 = dict1['callback_data']
        callback_data2 = dict2['callback_data']

        if call.data.split()[0] == 'confirmation_button':
            markup = types.InlineKeyboardMarkup()
            confirmation_button = types.InlineKeyboardButton(f'✅ {total_voted0 + 1}/{total_members}',
                                                             callback_data=callback_data0)
            again_button = types.InlineKeyboardButton(f'🔄 {total_voted1}/{total_members}', callback_data=callback_data1)
            block_button = types.InlineKeyboardButton(f'❌ {total_voted2}/{total_members}', callback_data=callback_data2)
            markup.add(confirmation_button, again_button, block_button)
            artist_confirmation[artist_id][1] = bot.edit_message_reply_markup(chat_id=GetChannelId(),
                                                                              message_id=message2.message_id,
                                                                              reply_markup=markup)
            total_voted0 += 1
        elif call.data.split()[0] == 'again_button':
            markup = types.InlineKeyboardMarkup()
            confirmation_button = types.InlineKeyboardButton(f'✅ {total_voted0}/{total_members}',
                                                             callback_data=callback_data0)
            again_button = types.InlineKeyboardButton(f'🔄 {total_voted1 + 1}/{total_members}',
                                                      callback_data=callback_data1)
            block_button = types.InlineKeyboardButton(f'❌ {total_voted2}/{total_members}', callback_data=callback_data2)
            markup.add(confirmation_button, again_button, block_button)
            artist_confirmation[artist_id][1] = bot.edit_message_reply_markup(chat_id=GetChannelId(),
                                                                              message_id=message2.message_id,
                                                                              reply_markup=markup)
            total_voted1 += 1
        elif call.data.split()[0] == 'block_button':
            markup = types.InlineKeyboardMarkup()
            confirmation_button = types.InlineKeyboardButton(f'✅ {total_voted0}/{total_members}',
                                                             callback_data=callback_data0)
            again_button = types.InlineKeyboardButton(f'🔄 {total_voted1}/{total_members}', callback_data=callback_data1)
            block_button = types.InlineKeyboardButton(f'❌ {total_voted2 + 1}/{total_members}',
                                                      callback_data=callback_data2)
            markup.add(confirmation_button, again_button, block_button)
            artist_confirmation[artist_id][1] = bot.edit_message_reply_markup(chat_id=GetChannelId(),
                                                                              message_id=message2.message_id,
                                                                              reply_markup=markup)
            total_voted2 += 1

        total_voted = total_voted0 + total_voted1 + total_voted2

        message_and_admin_dict[message2_id].append(admin_id)

        if total_voted == total_members:
            sollution(total_voted0, total_voted1, total_voted2, artist_id, artist_name, user_name, message1, message2)

    else:
        bot.send_message(admin_id, "Проголосовать можно только один раз ♿")


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
