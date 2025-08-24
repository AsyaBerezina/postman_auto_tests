
"""
Задание по автотестированию

Тестирует различные типы HTTP запросов к сервису postman-echo.com
для проверки корректности обработки GET и POST запросов.

Автор: Березина Анастасия
"""

import json
import pytest
import requests
from datetime import datetime
from typing import Dict, Any


class TestPostmanEcho:
    """Класс с тестами для Postman Echo API."""
    
    BASE_URL = "https://postman-echo.com"
    TIMEOUT = 30
    
    @pytest.fixture(autouse=True)
    def setup_session(self):
        self.session = requests.Session()
        self.session.timeout = self.TIMEOUT
        
        self.session.headers.update({
            'User-Agent': 'PostmanEcho-AutoTest/1.0',
            'Accept': 'application/json'
        })
    
    def test_get_basic_request(self):
        """
        Тест 1: Базовый GET запрос без параметров.
        
        Проверяет:
        - Статус код 200
        - Наличие обязательных полей в ответе
        - Корректность структуры JSON ответа
        """
        # Отправляем GET запрос
        response = self.session.get(f"{self.BASE_URL}/get")
        
        # Проверяем статус код
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        assert response.headers.get('content-type').startswith('application/json'), \
            "Ответ должен быть в JSON формате"
        
        data = response.json()
        
        # Проверяем обязательные поля
        assert 'args' in data, "В ответе должно быть поле 'args'"
        assert 'headers' in data, "В ответе должно быть поле 'headers'"
        assert 'url' in data, "В ответе должно быть поле 'url'"
        
        assert data['url'] == f"{self.BASE_URL}/get", f"URL в ответе не совпадает: {data['url']}"
        
        assert data['args'] == {}, "Args должен быть пустым для запроса без параметров"
    
    def test_get_with_query_parameters(self):
        """
        Тест 2: GET запрос с query параметрами.
        
        Проверяет:
        - Корректную передачу query параметров
        - Различные типы данных в параметрах
        - Кодировку специальных символов
        """
        test_params = {
            'name': 'Иван Иванов',  
            'age': '29',            
            'city': 'Moscow',     
            'is_student': 'false',  
            'email': 'test@example.com'
        }
        
        response = self.session.get(f"{self.BASE_URL}/get", params=test_params)
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        
        returned_args = data['args']
        
        for key, expected_value in test_params.items():
            assert key in returned_args, f"Параметр '{key}' не найден в ответе"
            assert returned_args[key] == expected_value, \
                f"Параметр '{key}': ожидалось '{expected_value}', получено '{returned_args[key]}'"
        
        assert '?' in data['url'], "URL должен содержать query параметры"
    
    def test_post_json_data(self):
        """
        Тест 3: POST запрос с JSON данными.
        
        Проверяет:
        - Отправку JSON в теле запроса
        - Корректное echo JSON данных
        - Обработку вложенных объектов и массивов
        """
        test_data = {
            'user': {
                'id': 12345,
                'name': 'Тестовый Пользователь',
                'profile': {
                    'age': 30,
                    'city': 'Санкт-Петербург',
                    'interests': ['programming', 'testing', 'automation']
                }
            },
            'timestamp': datetime.now().isoformat(),
            'test_type': 'json_post_test',
            'numbers': [1, 2, 3, 4, 5],
            'boolean_flag': True,
            'null_value': None
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/post",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        
        assert 'data' in data, "В ответе должно быть поле 'data'"
        assert 'json' in data, "В ответе должно быть поле 'json'"
        assert 'headers' in data, "В ответе должно быть поле 'headers'"
        
        returned_json = data['json']
        assert returned_json == test_data, "Возвращённые JSON данные не совпадают с отправленными"
        
        headers = data['headers']
        assert 'content-type' in headers, "Заголовок Content-Type должен присутствовать"
        assert 'application/json' in headers['content-type'], \
            "Content-Type должен содержать application/json"
    
    def test_post_form_data(self):
        """
        Тест 4: POST запрос с form-data.
        
        Проверяет:
        - Отправку данных в формате application/x-www-form-urlencoded
        - Корректную обработку форм
        - Специальные символы в form-data
        """
        form_data = {
            'username': 'test_user_123',
            'password': 'SecurePassword!@#',
            'email': 'user@тест.рф', 
            'age': '28',
            'terms_accepted': 'on',
            'comments': 'Комментарий с кириллицей и спецсимволами: !@#$%^&*()'
        }
        
        response = self.session.post(f"{self.BASE_URL}/post", data=form_data)
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        
        assert 'form' in data, "В ответе должно быть поле 'form'"
        
        returned_form = data['form']
        
        for key, expected_value in form_data.items():
            assert key in returned_form, f"Поле формы '{key}' не найдено в ответе"
            assert returned_form[key] == expected_value, \
                f"Поле '{key}': ожидалось '{expected_value}', получено '{returned_form[key]}'"
        
        headers = data['headers']
        assert 'content-type' in headers, "Заголовок Content-Type должен присутствовать"
        assert 'application/x-www-form-urlencoded' in headers['content-type'], \
            "Content-Type должен содержать application/x-www-form-urlencoded"
    
    def test_get_with_custom_headers(self):
        """
        Тест 5: GET запрос с кастомными заголовками.
        
        Проверяет:
        - Передачу пользовательских заголовков
        - Echo пользовательских заголовков в ответе
        - Обработку заголовков с спецсимволами
        """
        custom_headers = {
            'X-Test-Header': 'TestValue123',
            'X-User-Agent': 'CustomAgent/1.0',
            'X-Request-ID': 'req_' + str(int(datetime.now().timestamp())),
            'X-Client-Version': '2.1.0',
            'X-Special-Chars': 'Value with spaces and symbols: !@#$%'
        }
        
        response = self.session.get(f"{self.BASE_URL}/get", headers=custom_headers)
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        
        assert 'headers' in data, "В ответе должно быть поле 'headers'"
        
        returned_headers = data['headers']
        
        for header_name, expected_value in custom_headers.items():
            header_name_lower = header_name.lower()
            
            assert header_name_lower in returned_headers, \
                f"Заголовок '{header_name}' не найден в ответе"
            assert returned_headers[header_name_lower] == expected_value, \
                f"Заголовок '{header_name}': ожидалось '{expected_value}', " \
                f"получено '{returned_headers[header_name_lower]}'"
    

    def test_get_with_multiple_query_parameters(self):
        """
        Тест 6: GET запрос с множественными query параметрами.
        
        Проверяет:
        - Передачу большого количества параметров
        - Различные типы значений в параметрах
        - Корректную обработку массивов в query string
        """
        query_params = {
            'search': 'python testing',
            'category': 'programming',
            'level': 'advanced',
            'duration_min': '30',
            'duration_max': '120',
            'language': 'ru',
            'format': 'json',
            'sort_by': 'relevance',
            'order': 'desc',
            'page': '1',
            'limit': '20',
            'include_archived': 'false',
            'tags': 'api,testing,automation'
        }
        
        response = self.session.get(f"{self.BASE_URL}/get", params=query_params)
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        
        data = response.json()
        
        returned_args = data['args']
        
        assert len(returned_args) == len(query_params), \
            f"Количество параметров не совпадает: ожидалось {len(query_params)}, получено {len(returned_args)}"
        
        for param_name, expected_value in query_params.items():
            assert param_name in returned_args, f"Параметр '{param_name}' не найден в ответе"
            assert returned_args[param_name] == expected_value, \
                f"Параметр '{param_name}': ожидалось '{expected_value}', получено '{returned_args[param_name]}'"
        
        url = data['url']
        for param_name in query_params.keys():
            assert param_name in url, f"Параметр '{param_name}' не найден в URL: {url}"
    


class TestPostmanEchoNegative:
    """Класс с негативными тестами для Postman Echo API."""
    
    BASE_URL = "https://postman-echo.com"
    TIMEOUT = 30
    
    @pytest.fixture(autouse=True)
    def setup_session(self):
        """Настройка сессии для негативных тестов."""
        self.session = requests.Session()
        self.session.timeout = self.TIMEOUT
    
    def test_invalid_endpoint(self):
        """
        Тест 7: Запрос к несуществующему endpoint.
        
        Проверяет:
        - Корректную обработку 404 ошибок
        - Структуру ответа при ошибке
        """
        response = self.session.get(f"{self.BASE_URL}/nonexistent-endpoint")
        
        assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
        
        assert len(response.content) > 0, "Ответ не должен быть пустым даже при 404"


pytest_plugins = []


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


@pytest.fixture(scope="session")
def api_base_url():
    """Фикстура с базовым URL API."""
    return "https://postman-echo.com"


@pytest.fixture
def test_timestamp():
    """Фикстура с временной меткой для тестов."""
    return datetime.now().isoformat()


@pytest.fixture
def sample_user_data():
    """Фикстура с тестовыми данными пользователя."""
    return {
        'id': 12345,
        'name': 'Тестовый Пользователь',
        'email': 'test@example.com',
        'age': 25,
        'city': 'Москва'
    }