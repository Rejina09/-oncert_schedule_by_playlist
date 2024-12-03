from http.client import InvalidURL

from yandex_music import Client
import requests
import re

def is_valid_playlist_url(url):
    pattern = r'^https://music\.yandex\.ru/users/([a-zA-Z0-9_-]+)/playlists/(\d+)(\?utm_medium=copy_link)?$'
    match = re.match(pattern, url)
    if "yandex.ru" not in url:
        raise InvalidURL("Ссылка на плейлист не с Яндекс музыки")
    if match:
        return True
    else:
        raise InvalidURL("Некорректный формат ссылки")

def get_playlist_artists(playlist_url, token):
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
        if len(artists) >= 5:
            break
    return list(artists)[:5]

#playlist_url = "https://music.yandex.ru/users/sheiniljusha/playlists/1037?utm_medium=copy_link"
#token = "y0_AgAAAABgq2O1AAG8XgAAAAD6-nL2AAABk9x-o1lEt40j_7E_BFi3l6JBSQ"
#artists = get_playlist_artists(playlist_url, token)
#print("Артисты из плейлиста:")
#print("\n".join(artists))
