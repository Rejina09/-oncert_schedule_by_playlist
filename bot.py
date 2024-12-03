import aiogram
import telebot
from aiogram import Dispatcher
from telebot import types


from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from Playlist import is_valid_playlist_url, InvalidURL, get_playlist_artists

bot = telebot.TeleBot('7339494316:AAHf7NnH5rd3RF9sQdPQrs7Qzrmrg_rrOe4');

#searcher = ConcertSearcher()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Получить список концертов.")
    button1 = types.KeyboardButton("/start")
    markup.add(button)
    markup.add(button1)

    bot.send_message(message.chat.id, 'Нажмите на кнопку "Получить список концертов" если вы хотите получить список концертов', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Получить список концертов.")
def button_response(message):
    bot.send_message(message.from_user.id, "Привет! Я могу помочь тебе спланировать твой досуг. \n Пришли мне ссылку на свой плейлист в Яндекс.Музыке, а я отправлю тебе возможные концерты!");
    bot.register_next_step_handler(message, playlist)

@bot.message_handler(func=lambda message: True)
def handle_response(message):
    if message.text == 'Да, я пришлю новую ссылку.':
        bot.send_message(message.chat.id, "Пожалуйста пришлите ссылку.")
        bot.register_next_step_handler(message, playlist)
    elif message.text == 'Нет, остановить работу бота.':
        bot.send_message(message.chat.id, "Обращайтесь, когда мы вам понадобимся!")


@bot.message_handler(content_types=['text'])
def playlist(message):
    playlist_link = message.text
    try:
        if is_valid_playlist_url(playlist_link):
            bot.send_message(message.from_user.id,
                             "Я обрабатываю ваш запрос, это может занять немного времени:)")

            artists = get_playlist_artists( playlist_link, "y0_AgAAAABgq2O1AAG8XgAAAAD6-nL2AAABk9x-o1lEt40j_7E_BFi3l6JBSQ")
            concerts(message, artists)

    except InvalidURL as e:
        if "не с Яндекс музыки" in str(e):
            bot.send_message(message.from_user.id,
                             "К сожалению, в данный момент мы работаем только с плейлистами на Яндекс.Музыке.");
            error_playlist(message)
        elif "Некорректный формат ссылки" in str(e):
            bot.send_message(message.from_user.id,
                             "Вы направили некорректный формат ссылки.");
            error_playlist(message)
        else:
            bot.send_message(message.from_user.id,
                             "Вы направили некорректный формат ссылки.");
            error_playlist(message)

def error_playlist (message):
    keyboard = types.ReplyKeyboardMarkup();
    key_yes = types.KeyboardButton(text='Да, я пришлю новую ссылку.')
    keyboard.add(key_yes)
    key_no = types.KeyboardButton(text='Нет, остановить работу бота.')
    keyboard.add(key_no)
    button1 = types.KeyboardButton("/start")
    keyboard.add(button1)
    question = 'Хотите ли вы заменить ссылку?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

def concerts (message, artists):
    for artist_name in artists:
        concerts = searcher.find_concerts(artist_name)
        bot.send_message(message.from_user.id, text='У артиста' + artist_name + 'есть следующие концерты:')
        s = ''
        for concert in concerts:
            s = s + 'Концерт' + concert.data + '\n Место:' + concert.place + '\n Ссылка на покупку билета:' + concert.tickets_url + '\n \n'
        bot.send_message(message.from_user.id, text=s)














bot.polling(none_stop=True, interval=0)