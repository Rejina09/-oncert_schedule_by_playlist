from yandex_music import Client
import re
import logging
from http.client import InvalidURL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_playlist_url(url):
    pattern = r'^https://music\.yandex\.ru/users/([a-zA-Z0-9!"#$%&()*+,\-./:;<=>?@\[\\\]^_`{|}~]+)/playlists/(\d+)(\?utm_medium=copy_link)?$'
    match = re.match(pattern, url)
    if "yandex.ru" not in url:
        raise InvalidURL("Ссылка на плейлист не с Яндекс музыки")
    if match:
        return True
    else:
        raise InvalidURL("Некорректный формат ссылки")

def get_playlist_artists(playlist_url, token, count):
    try:
        client = Client(token).init()
        parts = playlist_url.strip('/').split('/')
        user_id = parts[-3]
        playlist_id = parts[-1]
        playlist = client.users_playlists(playlist_id, user_id)
        artists = set()
        for track_short in playlist.tracks:
            track = track_short.fetch_track()
            if track.artists:
                artists.update(artist.name for artist in track.artists)
            if len(artists) >= count:
                break
        logging.info(f"Извлечённые артисты из плейлиста: {artists}")
        return list(artists)[:count]
    except Exception as e:
        logging.error(f"Ошибка при получении артистов из плейлиста: {e}")
        raise


p = "https://music.yandex.ru/users/Ender.Wiggin.2017/playlists/1068"
cu = (get_playlist_artists(p, "y0_AgAAAABgq2O1AAG8XgAAAAD6-nL2AAABk9x-o1lEt40j_7E_BFi3l6JBSQ", 5))
print(is_valid_playlist_url(p))

p1 = "https://music.yandex.ru/users/yalalka977/playlists/102"
print(is_valid_playlist_url(p1))
