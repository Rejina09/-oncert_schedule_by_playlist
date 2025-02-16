# Yandex Music Concert Schedule Bot

Этот бот для Telegram принимает ссылку на плейлист Яндекс Музыки и возвращает список концертов исполнителей из плейлиста. 

## Содержание
- [Структура проекта](#структура-проекта)
- [Сборка](#сборка)
- [Для пользователей](#для-пользователей)
- [Тестирование](#тестирование)
- [To do](#to-do)
- [Команда проекта](#команда-проекта)

  
## Структура проекта

### [playlist.py](https://github.com/Rejina09/Concert_schedule_by_playlist/blob/main/playlist.py)
Файл содержит функцию ```is_valid_playlist_url```, принимающая ссылку и проверяющая ее на то, что она с Яндекс Музыки и ссылается на плейлист, и содержит функцию ```get_playlist_artists```, принимающая корректную ссылку на плейлист с Яндекс Музыки (проверенную функцией ```is_valid_playlist_url```) и выдающую список из не более чем пяти артистов, исполняющие первые треки в плейлисте. Если ссылка не корректная, то функция ```get_playlist_artists``` выдает ошибку.

### [test_playlist.py](https://github.com/Rejina09/Concert_schedule_by_playlist/blob/main/test_playlist.py)
Файл содержит тесты, проверяющие работу функций ```is_valid_playlist_url``` и ```get_playlist_artists```.

### [concert_searcher.py](https://github.com/Rejina09/Concert_schedule_by_playlist/blob/main/concert_searcher.py)
Файл содержит класс ```Concert``` для хранения информации о концерте, ```ConcertSearcher```, который автоматически запускает web движок Chrome, для парсинга концертов, используя библиотеку ```Selenium```; в классе ```ConcertSearcher```  метод ```search_concerts```, который принимает на вход название исполнителя и возвращает список его концертов. А также служебная функция ```extract_concert_info_for_afisha_ru``` для извлечения информации о концерте из строки с информцией о концерте спарсенной с сайта afisha.ru. Тукже настроен логгер.

### [test_concert_searcher.py](https://github.com/Rejina09/Concert_schedule_by_playlist/blob/main/test_concert_searcher.py)
Файл содержит тесты для проверки работы класса ```ConcertSearcher```, функции ```search_concerts``` и ```extract_concert_info_for_afisha_ru```.

### [bot.py](https://github.com/Rejina09/Concert_schedule_by_playlist/blob/main/bot.py)
Файл содержит код бота. Там прописаны все операции, отправляющие и принимающие сообщения от пользователя. От пользователя бот принимает ссылку на плейлист, обрабатывает её и выводит концерты, обращаясь к функциям ```is_valid_playlist_url```, ```get_playlist_artists``` и ```search_concerts```.

###### (файлы с тестами лежат в отдельной ветке ```tests```)


## Сборка
Как установить, запустить от лица разработчика.

### Требования
Необходимо наличие некоторых библиотек и пакетов (указаны в ```requirements.txt``` ), которые можно установить с помощью ```pip install <package_name>``` .  Также необходимо установить webdriver для браузера Chrome, который можно скачать [здесь](https://chromedriver.chromium.org/downloads) (хотя обычно он установлен автоматически с браузером).

### Работа с токеном
Вам необходимо создать файл config.py, в котором будет токен на вашего бота и токен на аккаунт пользователя Яндекс.Музыки. Выглядеть он должен так:
```
TELEGRAM_API_TOKEN = "token_your_bot"

YANDEX_MUSIC_TOKEN = "token_your_account"
```
Где взять токен для бота? -
При создании бота он выдаётся автоматически.

Где взять токен на Яндекс.Музыку? -
Скачать одно из расширений в засисимости от используемого браузера.

[Для Google Chrome](https://chromewebstore.google.com/detail/yandex-music-token/lcbjeookjibfhjjopieifgjnhlegmkib?pli=1)

[Для Firefox](https://addons.mozilla.org/en-US/firefox/addon/yandex-music-token/)

Авторизорваться по одной из ссылок выше, скопировать полученный при регистрации токен.

### Запуск проекта
Запускаете файл bot.py и можете пользоваться ботом.

## Для пользователей
Необходимо начать работу с ботом с помощью команды ```\start```, передать ему ссылку на свой плейлист Яндекс.Музыки. Более подробный процесс работы с ботом можно увидеть [здесь](https://drive.google.com/file/d/1BE8hUgLY5ckMS5GE33efrkJi7DDHaWyx/view?usp=drive_link).

## Тестирование
Файлы с тестами находятся в отдельной ветке ```tests```.  
В файле [test_playlist.py](#test_playlist.py) содержатся тесты для [playlist.py](#playlist.py) .проверки обработки ссылки на плейлист и самого плейста.  
В файле [test_concert_searcher.py](#test_concert_searcher.py) содержатся тесты для [concert_searcher.py](#concert_searcher.py).

На гугл-диске содержатся [видеоотчет](https://drive.google.com/file/d/1BE8hUgLY5ckMS5GE33efrkJi7DDHaWyx/view?usp=drive_link) по тестированию работы нашего бота, [файл](https://docs.google.com/document/d/1A92xYJe9rlYYSt_doerm0t5KUxjPn9rurxx16zNw1BE/edit?tab=t.0) с фото-отчетом по тестированию работы бота, [видеоотчет](https://drive.google.com/file/d/10lFCnpHITtT_FWFlqPJqIvQNW_8BnVeA/view?usp=drive_link) тестирования кода Телеграм бота.

## To do
- [x] Телеграм бот. 
- [x] Функция, обрабатывающая ссылки на корректность.
- [x] Функция, получающая ссылку на плейлист и возвращающая список из первых 5 исполнителей.
- [x] Класс, ищущий концерты по имени исполнителя.
- [x] Написать README
- [x] Добавить кнопки в Телеграмм бот для дополнительных опций (выбор количества исполнителей).
- [x] Написать логику для того, чтобы выдавать концерты по исполнителю.
- [x] Доработать парсинг концертов: добавить возможность парсить концерты с других сайтов для улучшения стабильности работы и уменьшения вероятности капчи и прочего.
- [ ] ...
- [ ] Получить 10:)

## Команда проекта
![image](https://github.com/user-attachments/assets/b4b66617-0376-458c-a155-61769e2488c6)

- [Илья Шеин](https://t.me/ilya_shn) — парсинг концертов по названию исполнителей, настройка сервера с итоговым ботом.
- [Маргарита Самородова](https://t.me/sam_vader) — анализ плейлиста по ссылке с Яндекс Музыки.
- [Регина Сабирьянова](https://t.me/rejinasab) — работа в создании тг-бота (в основном логика работы с пользователем).
- [Мария Дёминова](https://t.me/mariaskai13) — работа в создании тг-бота (в основном создание кнопок для пользователя).

