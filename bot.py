# bot.py

import telebot
from telebot import types
import logging
import threading
import random
import time

from playlist import is_valid_playlist_url, InvalidURL, get_playlist_artists
from concert_searcher import ConcertSearcher
import config


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Установите токены здесь из файла config.py (он должен быть в той же директории, что и этот файл и добавлен самостоятельно локально)
TELEGRAM_API_TOKEN = config.TELEGRAM_API_TOKEN
YANDEX_MUSIC_TOKEN = config.YANDEX_MUSIC_TOKEN


if not TELEGRAM_API_TOKEN:
    logging.error("Токен Telegram API не установлен.")
    exit(1)

if not YANDEX_MUSIC_TOKEN:
    logging.error("Токен Yandex Music не установлен.")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

searcher = ConcertSearcher()
search_lock = threading.Lock()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Получить список концертов.")
    markup.add(button)

    bot.send_message(
        message.chat.id,
        'Нажмите на кнопку "Получить список концертов", если вы хотите получить список концертов.',
        reply_markup=markup
    )
    logging.info(f"Пользователь {message.from_user.id} начал работу с ботом.")

@bot.message_handler(func=lambda message: message.text == "Получить список концертов.")
def button_response(message):
    bot.send_message(
        message.from_user.id,
        "Привет! Я могу помочь тебе спланировать твой досуг.\nПришли мне ссылку на свой плейлист в Яндекс.Музыке, а я отправлю тебе возможные концерты!"
    )
    bot.register_next_step_handler(message, playlist)
    logging.info(f"Пользователь {message.from_user.id} запросил список концертов.")

@bot.message_handler(func=lambda message: True)
def handle_response(message):
    if message.text == 'Да, я пришлю новую ссылку.':
        bot.send_message(message.chat.id, "Пожалуйста, пришлите ссылку.")
        bot.register_next_step_handler(message, playlist)
        logging.info(f"Пользователь {message.from_user.id} решил прислать новую ссылку.")
    elif message.text == 'Нет, остановить работу бота.':
        bot.send_message(message.from_user.id, "Обращайтесь, когда мы вам понадобятся!")
        logging.info(f"Пользователь {message.from_user.id} остановил работу бота.")

@bot.message_handler(content_types=['text'])
def playlist(message):
    playlist_link = message.text
    logging.info(f"Получена ссылка на плейлист от пользователя {message.from_user.id}: {playlist_link}")
    try:
        if is_valid_playlist_url(playlist_link):
            bot.send_message(message.from_user.id, "Я обрабатываю ваш запрос, это может занять немного времени :)")
            logging.info(f"Обработка плейлиста для пользователя {message.from_user.id}")

            artists = get_playlist_artists(playlist_link, YANDEX_MUSIC_TOKEN)
            logging.info(f"Извлечённые артисты: {artists}")
            concerts(message, artists)
    except InvalidURL as e:
        logging.warning(f"Неверная ссылка от пользователя {message.from_user.id}: {e}")
        if "не с Яндекс музыки" in str(e):
            bot.send_message(message.from_user.id, "К сожалению, в данный момент мы работаем только с плейлистами на Яндекс.Музыке.")
        elif "Некорректный формат ссылки" in str(e):
            bot.send_message(message.from_user.id, "Вы направили некорректный формат ссылки.")
        else:
            bot.send_message(message.from_user.id, "Вы направили некорректный формат ссылки.")
        error_playlist(message)

def error_playlist(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_yes = types.KeyboardButton(text='Да, я пришлю новую ссылку.')
    key_no = types.KeyboardButton(text='Нет, остановить работу бота.')
    keyboard.add(key_yes, key_no)
    button1 = types.KeyboardButton("/start")
    keyboard.add(button1)
    question = 'Хотите ли вы заменить ссылку?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    logging.info(f"Пользователю {message.from_user.id} предложено заменить ссылку.")

def concerts(message, artists):
    for artist_name in artists:
        try:
            with search_lock:
                concerts = searcher.search(artist_name)
            if concerts:
                response = f'У артиста {artist_name} есть следующие концерты:\n\n'
                for concert in concerts:
                    response += f"{concert}\n\n"
            else:
                response = f'Концерты для артиста {artist_name} не найдены.\n\n'

            bot.send_message(message.from_user.id, text=response)
            logging.info(f"Отправлены концерты для артиста {artist_name} пользователю {message.from_user.id}")

            # Добавление случайной задержки между поисками
            delay = random.uniform(1, 3)  # Задержка от 1 до 3 секунд
            logging.info(f"Задержка перед следующим поиском: {delay:.2f} секунд.")
            time.sleep(delay)
        except Exception as e:
            logging.error(f"Ошибка при обработке концертов для {artist_name}: {e}")
            bot.send_message(message.from_user.id, text=f"Произошла ошибка при поиске концертов для {artist_name}.")

if __name__ == '__main__':
    try:
        logging.info("Бот начал работу.")
        bot.polling(none_stop=True, interval=0)
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную.")
    finally:
        searcher.close()
        logging.info("Бот завершил работу.")
