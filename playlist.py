from yandex_music import Client
import re
import logging
from http.client import InvalidURL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_playlist_url(url):
    pattern1 = r'^https://music\.yandex\.ru/users/([a-zA-Z0-9!"#$%&()*+,\-./:;<=>?@\[\\\]^_`{|}~]+)/playlists/(\d+)(\?utm_medium=copy_link)?$'
    pattern2 = r'^https://next\.music\.yandex\.ru/playlists/([a-f0-9\-]+)(\?utm_medium=copy_link)?$'
    match1 = re.match(pattern1, url)
    match2 = re.match(pattern2, url)
    if "yandex.ru" not in url:
        raise InvalidURL("Ссылка на плейлист не с Яндекс музыки")
    if match1 or match2:
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
