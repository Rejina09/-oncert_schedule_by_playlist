from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

import logging
import time
import random
from queue import Queue

logger = logging.getLogger(__name__)


class SearchServiceOrder:
    def __init__(self):
        self.__order = Queue()
        self.__order.put("afisha.ru")
        self.__order.put("kassir.ru")
        self.__order.put("live.mts.ru")

    def get_service(self):
        prev_first = self.__order.get()
        self.__order.put(prev_first)
        return prev_first

    def __len__(self):
        return self.__order.qsize()

    def add_service(self, service):
        if service not in list(self.__order.queue):
            self.__order.put(service)

    def remove_service(self, service):
        if service in list(self.__order.queue):
            self.__order.queue.remove(service)

    def __str__(self):
        return str(list(self.__order.queue))


class Concert:
    def __init__(self, artist, date, city, place, concert_url):
        self.artist = artist
        self.date = date
        self.city = city
        self.place = place
        self.tickets_url = concert_url

    def __str__(self):
        return f"Дата: {self.date}\nГород: {self.city}\nПлощадка: {self.place}\nСсылка: {self.tickets_url}"


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G996B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/99.0.4844.84 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/14.6 Mobile/15E148 Safari/604.1"
]


class ConcertSearcher:
    def __init__(self):
        chrome_options = Options()
        # при необходимости можно раскомментировать headless режим
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")

        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f"user-agent={user_agent}")

        try:
            self.__driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.__driver, 10)  # таймаут для WebDriverWait — 10 секунд
            logger.info("WebDriver инициализирован.")
        except Exception as e:
            logger.error(f"Не удалось инициализировать WebDriver: {e}")
            raise RuntimeError("Не удалось инициализировать WebDriver")

        self.__searcher_service_order = SearchServiceOrder()

        # Счётчик поисковых запросов для перезапуска Selenium
        self._requests_counter = 0

    def __del__(self):
        if self.__driver:
            try:
                self.__driver.quit()
                logger.info("WebDriver закрыт.")
            except Exception as e:
                logger.error(f"Ошибка при закрытии WebDriver: {e}")

    def restart_driver(self):
        """
        Перезапуск драйвера (закрываем текущий и инициализируем заново).
        """
        try:
            self.__driver.quit()
            logger.info("WebDriver остановлен для перезапуска.")
        except Exception as e:
            logger.error(f"Ошибка при закрытии WebDriver: {e}")

        # Заново инициализируем
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f"user-agent={user_agent}")
        self.__driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.__driver, 10)
        self._requests_counter = 0  # сброс счётчика
        logger.info("WebDriver переинициализирован.")

    def afishaRu_search(self, artist_name):
        logger.info(f"Начат поиск концертов для исполнителя: {artist_name} с помощью afisha.ru")
        search_url = f'https://www.afisha.ru/search/person/?query={artist_name}'
        concerts = []
        try:
            self.__driver.get(search_url)
            time.sleep(random.uniform(1, 2))  # небольшая рандомная пауза

            # Пробуем закрыть баннер (если появится)
            try:
                close_banner = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='popmechanic-close']"))
                )
                time.sleep(random.uniform(1, 2))
                close_banner.click()
            except:
                pass

            time.sleep(random.uniform(1, 2))

            # Ссылка на страницу артиста
            artist_page_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='CjnHd y8A5E vVS2J']"))
            )
            artist_page_link.click()
            time.sleep(random.uniform(1, 2))

            # Снова закрываем баннер, если он появился
            try:
                close_banner2 = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='popmechanic-close']"))
                )
                time.sleep(random.uniform(1, 2))
                close_banner2.click()
            except:
                pass

            time.sleep(random.uniform(1, 2))

            # Кнопка «Показать ещё», если есть
            try:
                show_more_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='L_ilg R1IVp Q8u7A']"))
                )
                time.sleep(random.uniform(1, 2))
                show_more_btn.click()
            except:
                pass

            # Собираем блоки концертов
            time.sleep(random.uniform(2, 3))
            concerts_list = self.__driver.find_elements(By.XPATH, "//div[@class='V5MWw']")
            for concert in concerts_list:
                try:
                    day = concert.find_element(By.XPATH, ".//div[@class='FkJAH']").text
                except:
                    day = "неизвестная дата"
                try:
                    month = concert.find_element(By.XPATH, ".//div[@class='MG0hJ']").text
                except:
                    month = "неизвестный месяц"
                try:
                    time_concert = concert.find_element(By.XPATH, ".//div[@class='u_84n']").text
                except:
                    time_concert = "неизвестное время"
                try:
                    venue = concert.find_element(By.XPATH, ".//a[@class='CjnHd y8A5E McO96']").text
                except:
                    venue = "неизвестная площадка"
                try:
                    city_block = concert.find_element(By.XPATH, ".//div[@class='rtbal It9Zd']").find_element(By.XPATH,
                                                                                                             ".//div[@class='rtbal It9Zd']").find_element(
                        By.XPATH, ".//div")
                    city = city_block.text if city_block else "неизвестный город"
                except:
                    city = "неизвестный город"
                try:
                    concert_link = concert.find_element(By.XPATH, ".//a[@class='TSKAc']").get_attribute("href")
                except:
                    concert_link = "нет ссылки"

                concerts.append(Concert(
                    artist=artist_name,
                    date=f"{day} {month} - {time_concert}",
                    city=city,
                    place=venue,
                    concert_url=concert_link
                ))
        except Exception as e:
            logger.error(f"Ошибка при поиске концертов для {artist_name} с помощью afisha.ru: {e}")
            return []
        return concerts

    def kassirRu_search(self, artist_name):
        logger.info(f"Начат поиск концертов для исполнителя: {artist_name} с помощью kassir.ru")
        search_url = f"https://kassir.ru/artists?keyword={artist_name}"
        concerts = []
        try:
            self.__driver.get(search_url)
            time.sleep(random.uniform(1, 2))

            # Переходим на страницу артиста (первый результат)
            artist_page = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//picture[@class='absolute left-0 max-h-[86px] min-h-[86px] "
                    "min-w-[86px] max-w-[86px] shrink-0 rounded-l-xl ui-picture']"
                ))
            )
            time.sleep(random.uniform(1, 2))
            artist_page.click()

            # Секция с концертами
            section_with_concerts = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//section[@class='ui-content ui-content-padding mb-10 flex flex-col gap-10']"
                ))
            )

            # Ищем списки концертов
            lists_with_concerts = section_with_concerts.find_elements(
                By.XPATH,
                "//ul[@class='rounded-xl border-none xs:border xs:border-neutral-200 xs:bg-white xs:px-5']"
            )

            for concerts_section in lists_with_concerts:
                concerts_list = concerts_section.find_elements(By.TAG_NAME, "li")
                for concert_el in concerts_list:
                    try:
                        date_time = "неизвестное время"
                        try:
                            date_time = concert_el.find_element(By.CLASS_NAME, "z-10").text
                        except:
                            pass

                        venue = "неизвестное место"
                        try:
                            venue = concert_el.find_element(
                                By.XPATH,
                                ".//div[@data-selenide='eventScheduleVenue']"
                            ).text
                        except:
                            pass

                        city = "Москва"
                        try:
                            city = concert_el.find_element(
                                By.XPATH,
                                ".//p[@class='line-clamp-1 text-sm text-neutral-500']"
                            ).text
                        except:
                            pass

                        link = "нет ссылки"
                        try:
                            link = concert_el.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except:
                            pass

                        concerts.append(Concert(
                            artist=artist_name,
                            date=date_time,
                            city=city,
                            place=venue,
                            concert_url=link
                        ))
                    except Exception as ee:
                        logger.error(f"Ошибка при обработке одного из концертов на kassir.ru: {ee}")
        except Exception as e:
            logger.error(f"Ошибка при поиске концертов для {artist_name} с помощью kassir.ru: {e}")

        return concerts

    def liveMtsRu_search(self, artist_name):
        logger.info(f"Начат поиск концертов для исполнителя: {artist_name} с помощью live.mts.ru")
        search_url = f"https://live.mts.ru/moscow/search/results?query={artist_name}&searchCategory=persons"
        concerts = []
        try:
            self.__driver.get(search_url)
            time.sleep(random.uniform(1, 2))

            # «Показать больше» (или переход на страницу артиста)
            button_to_artist_page = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//a[contains(@class, 'PersonSearchPreview_loadMoreButton')]"
                ))
            )
            time.sleep(random.uniform(1, 2))
            button_to_artist_page.click()

            time.sleep(random.uniform(2, 3))

            # Собираем список концертов
            concerts_list = self.__driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'DefaultEventsScheduleItem_container')]"
            )

            for concert_el in concerts_list:
                try:
                    day = "неизвестная дата"
                    try:
                        day = concert_el.find_element(
                            By.XPATH,
                            ".//span[contains(@class, 'DefaultEventsScheduleItem_day')]"
                        ).text
                    except:
                        pass

                    month = "неизвестный месяц"
                    try:
                        month = concert_el.find_element(
                            By.XPATH,
                            ".//span[contains(@class, 'DefaultEventsScheduleItem_month')]"
                        ).text
                    except:
                        pass

                    time_concert = "неизвестное время"
                    try:
                        time_concert = concert_el.find_element(
                            By.XPATH,
                            ".//span[contains(@class, 'DefaultEventsScheduleItem_time')]"
                        ).text
                    except:
                        pass

                    venue = "неизвестное место"
                    try:
                        venue = concert_el.find_element(
                            By.XPATH,
                            ".//a[contains(@class, 'DefaultEventsScheduleItem_venueTitle')]"
                        ).text
                    except:
                        pass

                    city = "неизвестный город"
                    try:
                        city = concert_el.find_element(
                            By.XPATH,
                            ".//span[contains(@class, 'DefaultEventsScheduleItem_venueRegion')]"
                        ).text
                    except:
                        pass

                    concert_link = "нет ссылки"
                    try:
                        concert_link = concert_el.find_element(
                            By.XPATH,
                            ".//a[contains(@class, 'DefaultEventsScheduleItem_title')]"
                        ).get_attribute("href")
                    except:
                        pass

                    concerts.append(Concert(
                        artist=artist_name,
                        date=f"{day} {month} - {time_concert}",
                        city=city,
                        place=venue,
                        concert_url=concert_link
                    ))
                except Exception as ee:
                    logger.error(f"Ошибка при обработке концерта на live.mts.ru: {ee}")

        except Exception as e:
            logger.error(f"Ошибка при поиске концертов для {artist_name} с помощью live.mts.ru: {e}")

        return concerts

    def search(self, artist_name):
        """
        Выполняет поиск концертов для заданного артиста.
        Раз в 20 поисковых запросов перезапускает драйвер.
        """
        # Инкремент счётчика поисков
        self._requests_counter += 1

        # Проверяем, не пора ли перезапустить драйвер
        if self._requests_counter >= 6:
            logger.info("Достигнут лимит в 20 запросов – перезапускаем WebDriver.")
            self.restart_driver()

        # Если вдруг нет сервисов
        if len(self.__searcher_service_order) == 0:
            logger.error("Нет доступных сервисов для поиска концертов.")
            return []

        service = self.__searcher_service_order.get_service()
        logger.info(f"Для поиска концертов используется {service}")

        concerts = []
        if service == "afisha.ru":
            concerts = self.afishaRu_search(artist_name)
        elif service == "kassir.ru":
            concerts = self.kassirRu_search(artist_name)
        elif service == "live.mts.ru":
            concerts = self.liveMtsRu_search(artist_name)

        return concerts
