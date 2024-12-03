# concert_searcher.py

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
from datetime import datetime
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_concert_info_for_afisha_ru(concert_info):
    date_pattern = r"(\d{1,2} [а-яА-Я]+ \d{4}), (\d{1,2} [а-яА-Я]+ в \d{1,2}:\d{2})"
    place_pattern = r", ([^,]+)$"

    month_mapping = {
        "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
        "мая": 5, "июня": 6, "июля": 7, "августа": 8,
        "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
    }

    date_match = re.search(date_pattern, concert_info)
    if date_match:
        day_month_year = date_match.group(1)
        time = date_match.group(2)

        try:
            day, month_name, year = re.split(r' ', day_month_year)
            month = month_mapping.get(month_name.lower())
            if not month:
                logging.warning(f"Неизвестное название месяца: {month_name}")
                return None, None
            concert_date = datetime.strptime(f"{day} {month} {year} {time.split('в')[-1].strip()}", "%d %m %Y %H:%M")
        except Exception as e:
            logging.error(f"Ошибка при парсинге даты: {e}")
            concert_date = None
    else:
        concert_date = None

    place_match = re.search(place_pattern, concert_info)
    concert_place = place_match.group(1) if place_match else None

    return concert_date, concert_place


class Concert:
    def __init__(self, artist, date, place, tickets_url=None):
        self.artist = artist
        self.date = date
        self.place = place
        self.tickets_url = tickets_url

    def __str__(self):
        if self.tickets_url:
            return f"Исполнитель: {self.artist} | Дата: {self.date.strftime('%d.%m.%Y %H:%M') if self.date else 'Неизвестно'} | Место: {self.place} | Билеты: {self.tickets_url}\n"
        else:
            return f"Исполнитель: {self.artist} | Дата: {self.date.strftime('%d.%m.%Y %H:%M') if self.date else 'Неизвестно'} | Место: {self.place}\n"


class ConcertSearcher:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            self.__driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.__driver, 10)
            logging.info("WebDriver инициализирован.")
        except Exception as e:
            logging.error(f"Не удалось инициализировать WebDriver: {e}")
            raise

    def close(self):
        if self.__driver:
            try:
                self.__driver.quit()
                logging.info("WebDriver закрыт.")
            except Exception as e:
                logging.error(f"Ошибка при закрытии WebDriver: {e}")

    def search(self, artist_name):
        logging.info(f"Поиск концертов для исполнителя: {artist_name}")
        search_url = f'https://www.afisha.ru/search/concert/?query={artist_name}&searchInAllCities=true'
        try:
            self.__driver.get(search_url)

            # Ожидание загрузки результатов
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.hmVRD.DiLyV')))

            html = self.__driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            not_filtered_res = soup.find_all('span', class_='hmVRD DiLyV')

            logging.info(f"Найдено элементов концертов: {len(not_filtered_res)} для {artist_name}")

            res = []
            for elem in not_filtered_res:
                if elem.text != "Концерт":
                    concert_info = elem.text
                    concert_date, concert_place = extract_concert_info_for_afisha_ru(concert_info)
                    concert = Concert(artist_name, concert_date, concert_place)
                    res.append(concert)
                    logging.info(f"Найден концерт: {concert}")
            logging.info(f"Найдено {len(res)} концертов для исполнителя: {artist_name}")
            return res
        except Exception as e:
            logging.error(f"Ошибка при поиске концертов для {artist_name}: {e}")
            return []
