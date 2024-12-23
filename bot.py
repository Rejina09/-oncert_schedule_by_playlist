import telebot
from telebot import types
from functools import partial
import logging
from logging.handlers import RotatingFileHandler
import threading
import random
import time

from Playlist.playlist import is_valid_playlist_url, InvalidURL, \
    get_playlist_artists
from Concert_Searcher.concert_searcher import ConcertSearcher
import config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    'bot.log',  # название файла лога
    maxBytes=2 * 1024 * 1024,  # 2 MB
    backupCount=1
)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Установите токены здесь из файла config.py
TELEGRAM_API_TOKEN = config.TELEGRAM_API_TOKEN
YANDEX_MUSIC_TOKEN = config.YANDEX_MUSIC_TOKEN

if not TELEGRAM_API_TOKEN:
    logger.error("Токен Telegram API не установлен.")
    exit(1)

if not YANDEX_MUSIC_TOKEN:
    logger.error("Токен Yandex Music не установлен.")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

searcher = ConcertSearcher()
search_lock = threading.Lock()

# Хранение количества исполнителей для каждого пользователя
# Ключ: chat_id, Значение: int (число исполнителей)
user_num_concerts = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Получить список концертов.")
    markup.add(button)

    bot.send_message(
        message.chat.id,
        'Привет! Я могу помочь тебе спланировать твой досуг.\n'
        'Нажми на кнопку "Получить список концертов", если хочешь получить список концертов.',
        reply_markup=markup
    )
    logger.info(f"Пользователь {message.from_user.id} начал работу с ботом.")


@bot.message_handler(func=lambda message: message.text == "Получить список концертов.")
def concert_filters(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_yes = types.KeyboardButton(text='Да, хочу задать число исполнителей.')
    key_no = types.KeyboardButton(text='Нет, произвольные 5 подойдут.')
    keyboard.add(key_yes, key_no)
    button1 = types.KeyboardButton("/start")
    keyboard.add(button1)
    question = 'Нужно ли ограничение на число исполнителей?\nИли пришлём произвольных 5 по умолчанию.'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    logger.info(f"Пользователю {message.from_user.id} предложено наложить ограничения.")


@bot.message_handler(func=lambda message: message.text == "Нет, произвольные 5 подойдут.")
def button_response(message):
    # Сбрасываем/устанавливаем для данного пользователя число исполнителей в 5
    user_num_concerts[message.from_user.id] = 5
    bot.send_message(
        message.from_user.id,
        "Пришли мне ссылку на свой плейлист в Яндекс.Музыке, а я отправлю тебе список исполнителей!"
    )
    # Переходим на этап обработки ссылки
    bot.register_next_step_handler(message, playlist)
    logger.info(f"Пользователь {message.from_user.id} запросил список исполнителей (по умолчанию 5).")


@bot.message_handler(func=lambda message: message.text == "Да, хочу задать число исполнителей.")
def button_response(message):
    bot.send_message(
        message.from_user.id,
        "Введи предпочитаемое количество исполнителей."
    )
    bot.register_next_step_handler(message, handle_concerts_count)
    logger.info(f"Пользователь {message.from_user.id} хочет задать количество исполнителей.")


def handle_concerts_count(message):
    try:
        count = int(message.text)

        if count < 1 or count > 10:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            key_new = types.KeyboardButton(text='Ввести число заново.')
            key_default = types.KeyboardButton(text='Нет, произвольные 5 подойдут.')
            key_no = types.KeyboardButton(text='Нет, остановить работу бота.')
            keyboard.add(key_new, key_default, key_no)
            button1 = types.KeyboardButton("/start")
            keyboard.add(button1)

            question = 'Число не подходит по ограничениям:\nвыбери число от 1 до 10 или согласись на 5.'
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

            logger.info(f"Пользователю {message.from_user.id} предложено выбрать новое число или согласиться на 5.")
        else:
            # Сохраняем выбранное количество в словарь
            user_num_concerts[message.from_user.id] = count
            bot.send_message(message.from_user.id, f"Отлично! Пожалуйста, пришли ссылку на плейлист.")
            bot.register_next_step_handler(message, playlist)
            logger.info(f"Пользователь {message.from_user.id} выбрал число {count}.")
            logger.info(f"Пользователь {message.from_user.id} запросил список концертов.")

    except ValueError:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key_retry = types.KeyboardButton(text='Ввести число заново.')
        key_stop = types.KeyboardButton(text='Остановить работу бота.')
        keyboard.add(key_retry, key_stop)

        bot.send_message(
            message.from_user.id,
            "Пожалуйста, введи число или прекрати работу с ботом.",
            reply_markup=keyboard
        )

        logger.error(f"Пользователь {message.from_user.id} ввёл некорректные данные.")


@bot.message_handler(func=lambda message: message.text == "Ввести число заново.")
def retry_number(message):
    bot.send_message(
        message.from_user.id,
        "Введи предпочитаемое количество исполнителей."
    )
    bot.register_next_step_handler(message, handle_concerts_count)
    logger.info(f"Пользователь {message.from_user.id} решил ввести число заново.")


@bot.message_handler(func=lambda message: message.text == "Остановить работу бота.")
def stop_bot(message):
    bot.send_message(message.from_user.id, "Работа бота остановлена.")
    logger.info(f"Пользователь {message.from_user.id} остановил работу бота.")


@bot.message_handler(func=lambda message: True)
def handle_response(message):
    if message.text == 'Да, я пришлю новую ссылку.':
        bot.send_message(message.chat.id, "Пожалуйста, пришли ссылку.")
        bot.register_next_step_handler(message, playlist)
        logger.info(f"Пользователь {message.from_user.id} решил прислать новую ссылку.")
    elif message.text == 'Нет, остановить работу бота.':
        bot.send_message(message.from_user.id, "Обращайся, когда мы тебе понадобимся!")
        logger.info(f"Пользователь {message.from_user.id} остановил работу бота.")


def playlist(message):
    playlist_link = message.text
    logger.info(f"Получена ссылка на плейлист от пользователя {message.from_user.id}: {playlist_link}")

    # Берём число исполнителей, сохранённое в словаре; по умолчанию — 5
    count = user_num_concerts.get(message.from_user.id, 5)

    try:
        if is_valid_playlist_url(playlist_link):
            bot.send_message(message.from_user.id, "Я обрабатываю твой запрос, это может занять немного времени :)")
            logger.info(f"Обработка плейлиста для пользователя {message.from_user.id}")

            artists = get_playlist_artists(playlist_link, YANDEX_MUSIC_TOKEN, count)
            logger.info(f"Извлечённые артисты: {artists}")

            send_artist_keyboard(message, artists)
    except InvalidURL as e:
        logger.warning(f"Неверная ссылка от пользователя {message.from_user.id}: {e}")
        if "не с Яндекс музыки" in str(e):
            bot.send_message(message.from_user.id,
                             "К сожалению, в данный момент мы работаем только с плейлистами на Яндекс.Музыке.")
        elif "Некорректный формат ссылки" in str(e):
            bot.send_message(message.from_user.id, "Ты направил некорректный формат ссылки.")
        else:
            bot.send_message(message.from_user.id, "Ты направил некорректный формат ссылки.")
        error_playlist(message)


def handle_artist_selection(message, artists):
    selected_artist = message.text

    if selected_artist == "Нет, остановить работу бота.":
        bot.send_message(message.from_user.id, "Спасибо за использование бота! Возвращайся к нам снова:)")
        return

    if selected_artist in artists:
        bot.send_message(message.from_user.id, f"Ты выбрал артиста: {selected_artist}. Я проверю его концерты.")
        concerts(message, [selected_artist])

        remaining_artists = [artist for artist in artists if artist != selected_artist]

        if remaining_artists:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for artist in remaining_artists:
                keyboard.add(types.KeyboardButton(text=artist))

            keyboard.add(types.KeyboardButton(text="Нет, остановить работу бота."))
            keyboard.add(types.KeyboardButton(text="/start"))

            bot.send_message(
                message.from_user.id,
                "Можешь выбрать ещё одного артиста или приостановить работу.",
                reply_markup=keyboard
            )

            bot.register_next_step_handler(message, handle_artist_selection, remaining_artists)
        else:
            bot.send_message(message.from_user.id, "Все артисты были обработаны. Спасибо за использование бота!")
    else:
        bot.send_message(message.from_user.id, "Выбранный артист не найден в списке. Попробуйте ещё раз.")
        send_artist_keyboard(message, artists)


def send_artist_keyboard(message, artists):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for artist in artists:
        keyboard.add(types.KeyboardButton(text=artist))

    keyboard.add(types.KeyboardButton(text="Завершить"))
    keyboard.add(types.KeyboardButton(text="/start"))

    bot.send_message(
        message.from_user.id,
        "Выбери артиста из списка:",
        reply_markup=keyboard
    )

    bot.register_next_step_handler(message, handle_artist_selection, artists)


def error_playlist(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_yes = types.KeyboardButton(text='Да, я пришлю новую ссылку.')
    key_no = types.KeyboardButton(text='Нет, остановить работу бота.')
    keyboard.add(key_yes, key_no)
    button1 = types.KeyboardButton("/start")
    keyboard.add(button1)
    question = 'Хочешь заменить ссылку?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    logger.info(f"Пользователю {message.from_user.id} предложено заменить ссылку.")


def concerts(message, artists):
    for artist_name in artists:
        try:
            with search_lock:
                found_concerts = searcher.search(artist_name)
            if found_concerts:
                response = f'У артиста {artist_name} есть следующие концерты:\n\n'
                for concert_info in found_concerts:
                    response += f"{concert_info}\n\n"
            else:
                response = f'Концерты для артиста {artist_name} не найдены.\n\n'

            bot.send_message(message.from_user.id, text=response)
            logger.info(f"Отправлены концерты для артиста {artist_name} пользователю {message.from_user.id}")

            # Случайная задержка (опционально, можно убрать/оставить)
            delay = random.uniform(1, 3)
            logger.info(f"Задержка перед следующим поиском: {delay:.2f} секунд.")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"Ошибка при обработке концертов для {artist_name}: {e}")
            bot.send_message(message.from_user.id, text=f"Произошла ошибка при поиске концертов для {artist_name}.")


if __name__ == '__main__':
    try:
        logger.info("Бот начал работу.")
        bot.polling(none_stop=True, interval=1)
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
    finally:
        logger.info("Бот завершил работу.")
