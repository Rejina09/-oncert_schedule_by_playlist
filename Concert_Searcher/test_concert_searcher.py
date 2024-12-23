import pytest
from unittest.mock import MagicMock, patch

from concert_searcher import (
    SearchServiceOrder,
    Concert,
    ConcertSearcher
)

class TestSearchServiceOrder:
    def test_search_service_order_initial_size(self):
        """
        Проверяем, что по умолчанию в очереди три сервиса: afisha.ru, kassir.ru и live.mts.ru.
        """
        order = SearchServiceOrder()
        assert len(order) == 3
        assert str(order) == str(["afisha.ru", "kassir.ru", "live.mts.ru"])

    def test_get_service_rotates_queue(self):
        """
        Проверяем, что при вызове get_service() очередь «вращается»:
        первый сервис переходит в конец, а на следующий вызов get_service() уже выдаётся новый первый сервис.
        """
        order = SearchServiceOrder()

        first = order.get_service()
        assert first == "afisha.ru"
        second = order.get_service()
        assert second == "kassir.ru"

        third = order.get_service()
        assert third == "live.mts.ru"

        fourth = order.get_service()
        assert fourth == "afisha.ru"

    def test_add_service(self):
        """
        Проверяем добавление нового сервиса, которого изначально нет в очереди.
        """
        order = SearchServiceOrder()
        order.add_service("yandex.afisha")
        assert len(order) == 4
        assert str(order) == str(["afisha.ru", "kassir.ru", "live.mts.ru", "yandex.afisha"])

    def test_add_existing_service(self):
        """
        Если сервис уже есть в очереди, при повторном добавлении он не дублируется.
        """
        order = SearchServiceOrder()
        order.add_service("afisha.ru")
        assert len(order) == 3

    def test_remove_service(self):
        """
        Проверяем удаление существующего сервиса.
        """
        order = SearchServiceOrder()
        order.remove_service("kassir.ru")
        assert len(order) == 2
        assert str(order) == str(["afisha.ru", "live.mts.ru"])

    def test_remove_missing_service(self):
        """
        Если удаляемого сервиса нет, ничего не происходит, ошибок не бросается.
        """
        order = SearchServiceOrder()
        order.remove_service("unexisting.service")
        assert len(order) == 3
        assert str(order) == str(["afisha.ru", "kassir.ru", "live.mts.ru"])


class TestConcert:
    def test_concert_creation_and_str(self):
        """
        Тестируем, что объект Concert правильно создаётся
        и возвращает корректную строку при вызове str().
        """
        artist_name = "Artist"
        date = "10 октября - 20:00"
        city = "Москва"
        place = "Клуб XYZ"
        url = "https://example.com/tickets"

        concert = Concert(
            artist=artist_name,
            date=date,
            city=city,
            place=place,
            concert_url=url
        )

        assert concert.artist == artist_name
        assert concert.date == date
        assert concert.city == city
        assert concert.place == place
        assert concert.tickets_url == url

        concert_str = str(concert)
        assert "Дата: 10 октября - 20:00" in concert_str
        assert "Город: Москва" in concert_str
        assert "Площадка: Клуб XYZ" in concert_str
        assert "Ссылка: https://example.com/tickets" in concert_str


class TestConcertSearcher:
    """
    Здесь собраны тесты, связанные с ConcertSearcher и методами поиска на сайтах.
    Некоторые из них используют mock (unittest.mock) для подмены реального Selenium WebDriver.
    """

    @pytest.fixture
    def searcher_mocked(self):
        """
        Фикстура, возвращающая ConcertSearcher, у которого замокан WebDriver.
        """
        with patch("concert_searcher.webdriver.Chrome") as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver.return_value = mock_driver_instance

            searcher = ConcertSearcher()
            searcher._ConcertSearcher__driver = mock_driver_instance

            yield searcher

    def test_concert_searcher_no_services(self, caplog):
        """
        Проверяем, что при отсутствии сервисов в SearchServiceOrder
        мы получим соответствующий лог об ошибке и пустой список концертов.
        """
        with patch.object(SearchServiceOrder, '__len__', return_value=0):
            searcher = ConcertSearcher()
            result = searcher.search("SomeArtist")

            assert result == []
            assert any("Нет доступных сервисов" in message
                       for message in caplog.text.split("\n"))

    def test_concert_searcher_calls_afishaRu(self, searcher_mocked):
        """
        При первом вызове search() должен вызываться метод afishaRu_search().
        """
        with patch.object(searcher_mocked, 'afishaRu_search', return_value=[]) as mock_afisha:
            searcher_mocked.search("Artist")
            mock_afisha.assert_called_once_with("Artist")

    def test_concert_searcher_calls_kassirRu(self, searcher_mocked):
        """
        При втором вызове search() (после afisha.ru) должен вызываться метод kassirRu_search().
        """
        with patch.object(searcher_mocked, 'afishaRu_search', return_value=[]), \
             patch.object(searcher_mocked, 'kassirRu_search', return_value=[]) as mock_kassir:

            searcher_mocked.search("Artist")
            searcher_mocked.search("Artist")

            mock_kassir.assert_called_once_with("Artist")

    def test_concert_searcher_calls_liveMtsRu(self, searcher_mocked):
        """
        При третьем вызове search() (после afisha.ru, kassir.ru)
        должен вызываться метод liveMtsRu_search().
        """
        with patch.object(searcher_mocked, 'afishaRu_search', return_value=[]), \
             patch.object(searcher_mocked, 'kassirRu_search', return_value=[]), \
             patch.object(searcher_mocked, 'liveMtsRu_search', return_value=[]) as mock_mts:

            searcher_mocked.search("Artist")  # afisha.ru
            searcher_mocked.search("Artist")  # kassir.ru
            searcher_mocked.search("Artist")  # live.mts.ru

            mock_mts.assert_called_once_with("Artist")
