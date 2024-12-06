from playlist import is_valid_playlist_url, InvalidURL, get_playlist_artists
import config

def test_not_url():
    #Тестируем не ссылку
    try:
        is_valid_playlist_url("lalallalalalala")
    except InvalidURL as s:
        assert str(s) == "Ссылка на плейлист не с Яндекс музыки"

    try:
        is_valid_playlist_url("happy_new_year")
    except InvalidURL as s:
        assert str(s) == "Ссылка на плейлист не с Яндекс музыки"


def test_playlist_url_from_other_places():
    # Тестируем ссылки не с Яндекс Музыки
    try:
        is_valid_playlist_url("https://www.nyan.cat/")
    except InvalidURL as s:
        assert str(s) == "Ссылка на плейлист не с Яндекс музыки"

    try:
        is_valid_playlist_url("https://caos.myltsev.ru/lectures/")
    except InvalidURL as s:
        assert str(s) == "Ссылка на плейлист не с Яндекс музыки"

    try:
        is_valid_playlist_url("https://cpp.mazurok.com/page/37/")
    except InvalidURL as s:
        assert str(s) == "Ссылка на плейлист не с Яндекс музыки"

def test_сorrect_playlist_url():
    #Тестируем корректные ссылки
    assert is_valid_playlist_url("https://music.yandex.ru/users/yalalka977/playlists/102") == True
    assert is_valid_playlist_url("https://music.yandex.ru/users/music-blog/playlists/2131") == True
    assert is_valid_playlist_url("https://music.yandex.ru/users/sheiniljusha/playlists/1037?utm_medium=copy_link") == True
    assert is_valid_playlist_url("https://music.yandex.ru/users/yamusic-daily/playlists/153360693") == True

def test_not_correct_playlist_url():
    #Тестируем ссылки некорректного формата
    try:
        is_valid_playlist_url("https://music.yandex.ru/playlists/python_course_the_best")
    except InvalidURL as s:
        assert str(s) == "Некорректный формат ссылки"

    try:
        is_valid_playlist_url("https://music.yandex.ru/users/python_course_the_best!!!")
    except InvalidURL as s:
        assert str(s) == "Некорректный формат ссылки"

    try:
        is_valid_playlist_url("https://music.yandex.ru/we_love_python_and_timur_petrov")
    except InvalidURL as s:
        assert str(s) == "Некорректный формат ссылки"

def test_empty_string():
    #Тестируем пустую строку
    try:
        is_valid_playlist_url("")
    except InvalidURL as s:
        assert str(s) == "Ссылка на плейлист не с Яндекс музыки"


# Тестируем длину списка артистов
def test_len_playlist():
    #Тестируем плейлист с пятью исполнителями
    playlist_url1 = "https://music.yandex.ru/users/yalalka977/playlists/102"
    artists1 = get_playlist_artists(playlist_url1, config.YANDEX_MUSIC_TOKEN)
    assert 5 == len(artists1)

    #Тестируем плейлист с одним исполнителем
    playlist_url2 = "https://music.yandex.ru/users/yalalka977/playlists/1006"
    artists2 = get_playlist_artists(playlist_url2, config.YANDEX_MUSIC_TOKEN)
    assert 1 == len(artists2)

    #Тестируем плейлист со многими исполнителем
    playlist_url3 = "https://music.yandex.ru/users/yalalka977/playlists/3"
    artists3 = get_playlist_artists(playlist_url3, config.YANDEX_MUSIC_TOKEN)
    assert 5 == len(artists3)

def test_artists():
    #Тестируем на корректность списка артистов
    playlist_url1 = "https://music.yandex.ru/users/yalalka977/playlists/1007"
    artists1 = set(get_playlist_artists(playlist_url1, config.YANDEX_MUSIC_TOKEN))
    assert artists1 == set(["Альянс", 'Oxxxymiron', 'Монеточка', 'Aerosmith', 'Green Day'])

    playlist_url2 = 'https://music.yandex.ru/users/yalalka977/playlists/1008'
    artists2 = set(get_playlist_artists(playlist_url2, config.YANDEX_MUSIC_TOKEN))
    assert artists2 != ['Шаман']


# Запуск тестов
if __name__ == "__main__":
    test_not_url()
    test_playlist_url_from_other_places()
    test_сorrect_playlist_url()
    test_not_correct_playlist_url()
    test_empty_string()
    test_len_playlist()
    test_artists()
    print("Все тесты пройдены успешно!")
