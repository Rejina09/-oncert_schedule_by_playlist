# test_concert_searcher.py

import unittest
from unittest.mock import patch, MagicMock
from concert_searcher import extract_concert_info_for_afisha_ru, ConcertSearcher, Concert
from datetime import datetime


class TestConcertSearcher(unittest.TestCase):

    #тест функции extract_concert_info_for_afisha_ru с корректными данными
    def test_extract_concert_info_valid(self):
        concert_info = "21 декабря 2024, 21 декабря в 20:00, Барвиха Luxury Village"
        expected_date = datetime.strptime("21 12 2024 20:00", "%d %m %Y %H:%M")
        expected_place = "Барвиха Luxury Village"

        date, place = extract_concert_info_for_afisha_ru(concert_info)

        self.assertEqual(date, expected_date)
        self.assertEqual(place, expected_place)

    #тест функции extract_concert_info_for_afisha_ru с отсутствующим временем
    def test_extract_concert_info_missing_time(self):
        concert_info = "21 декабря 2024, 21 декабря, Барвиха Luxury Village"

        date, place = extract_concert_info_for_afisha_ru(concert_info)

        self.assertIsNone(date)
        self.assertEqual(place, "Барвиха Luxury Village")

    #тест функции extract_concert_info_for_afisha_ru с строкой неправильного формата
    def test_extract_concert_info_invalid_format(self):
        concert_info = "Некорректная строка без нужного формата"
        date, place = extract_concert_info_for_afisha_ru(concert_info)

        self.assertIsNone(date)
        self.assertIsNone(place)

    #тест функции extract_concert_info_for_afisha_ru с неизвестным месяцем
    def test_extract_concert_info_unknown_month(self):
        concert_info = "21 неизвестного_месяца 2024, 21 неизвестного_месяца в 20:00, Барвиха Luxury Village"
        date, place = extract_concert_info_for_afisha_ru(concert_info)

        self.assertIsNone(date)
        self.assertEqual(place, "Барвиха Luxury Village")

    #тест функции search с успешным поиском
    @patch('concert_searcher.webdriver.Chrome')
    def test_search_success(self, mock_webdriver):
        # Настройка мока для WebDriver
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver

        # Настройка мок-ответа страницы
        mock_driver.page_source = """
        <span class="hmVRD DiLyV">21 декабря 2024, 21 декабря в 20:00, Барвиха Luxury Village</span>
        <span class="hmVRD DiLyV">22 января 2025, 22 января в 19:30, Москва Concert Hall</span>
        """

        # Настройка ожидания
        mock_wait = MagicMock()
        mock_driver.wait = mock_wait
        mock_wait.until = MagicMock()

        searcher = ConcertSearcher()
        concerts = searcher.search("Тестовый Артист")

        self.assertEqual(len(concerts), 2)
        self.assertIsInstance(concerts[0], Concert)
        self.assertEqual(concerts[0].artist, "Тестовый Артист")
        self.assertEqual(concerts[0].place, "Барвиха Luxury Village")
        self.assertEqual(concerts[1].place, "Москва Concert Hall")
        self.assertEqual(concerts[1].date, datetime.strptime("22 01 2025 19:30", "%d %m %Y %H:%M"))

        searcher.close()

    #тест функции search с отсутствием концертов
    @patch('concert_searcher.webdriver.Chrome')
    def test_search_no_concerts(self, mock_webdriver):
        # Настройка мока для WebDriver
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver

        # Настройка мок-ответа страницы без концертов
        mock_driver.page_source = "<div>No concerts found.</div>"

        # Настройка ожидания
        mock_wait = MagicMock()
        mock_driver.wait = mock_wait
        mock_wait.until = MagicMock()

        searcher = ConcertSearcher()
        concerts = searcher.search("Неизвестный Артист")

        self.assertEqual(len(concerts), 0)

        searcher.close()

    #тест функции search с исключением
    @patch('concert_searcher.webdriver.Chrome')
    def test_search_exception(self, mock_webdriver):
        # Настройка мока для WebDriver, вызывающего исключение при get
        mock_driver = MagicMock()
        mock_driver.get.side_effect = Exception("Ошибка загрузки страницы")
        mock_webdriver.return_value = mock_driver

        searcher = ConcertSearcher()
        concerts = searcher.search("Артист с ошибкой")

        self.assertEqual(len(concerts), 0)

        searcher.close()


if __name__ == '__main__':
    unittest.main()
