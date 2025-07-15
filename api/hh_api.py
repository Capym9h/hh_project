import requests
import time
from typing import Dict, List, Optional, Any
from tqdm import tqdm
from config import BASE_URL, USER_AGENT, PER_PAGE, DEFAULT_TIME_DELAY


class HeadHunterAPI:
    """Класс для работы с API HH"""
    
    def __init__(self, user_agent: str = USER_AGENT, base_url: str = BASE_URL):
        self.base_url = base_url
        self.headers = {'User-Agent': user_agent}
        self.time_delay = DEFAULT_TIME_DELAY

    def set_time_delay(self, delay: float) -> None:
        """Установка задержки между запросами
        Param:
            delay: Задержка в секундах"""
        self.time_delay = delay 

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Выполнение запроса к api HH
        Param:
            url: URL для запроса
            params: Параметры запроса
        Returns:
            Ответ API в виде словаря"""
        
        time.sleep(self.time_delay)
        try:
            response = requests.get(url=url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'❌ Ошибка: Запрос к {url} вернул ошибку: {e}')
            return {}

    def search_vacancies(self, job_title: str, page: int = 0, per_page: int = PER_PAGE, 
                        only_with_salary: bool = True, locale: str = 'RU') -> Dict[str, Any]:
        """Поиск вакансий по названию
        Param:
            job_title: Название должности для поиска
            page: Номер страницы
            per_page: Количество вакансий на странице
            only_with_salary: Только вакансии с зарплатой
            locale: Локаль
        Returns:
            Результат поиска вакансий"""
        
        params = {
            'text': job_title,
            'search_field': 'name',
            'page': page,
            'per_page': per_page,
            'only_with_salary': only_with_salary,
            'locale': locale
        }
        return self._make_request(self.base_url, params)
    
    def get_vacancy_details(self, vacancy_id: str) -> Dict[str, Any]:
        """Получение полной информации о вакансии
        Param:
            vacancy_id: ID вакансии
        Returns:
            Полная информация о вакансии"""
        
        url = f"{self.base_url}/{vacancy_id}"
        return self._make_request(url)
    
    def get_vacancy_ids(self, job_title: str, max_pages: Optional[int] = None) -> List[str]:
        """Получение списка ID вакансий для заданной должности
        Param:
            job_title: Название должности
            max_pages: Максимальное количество страниц для парсинга
        Returns:
            Список ID вакансий"""
        
        vacancy_ids = []
        current_page = 0

        response = self.search_vacancies(job_title, page=current_page)
        
        if not response:
            print(f'❌ Ошибка: Не удалось получить вакансии по должности: {job_title}')
            return vacancy_ids
        
        total_vacancies = response.get('found', 0) #количество вакансий
        total_pages = response.get('pages', 0) #количество страниц с вакансиями
        
        print(f'Найдено {total_vacancies} вакансий по должности: "{job_title}" на {total_pages} страницах')
        
        if max_pages and max_pages < total_pages:
            total_pages = max_pages
            print(f'Limited to {max_pages} pages')
        
        # Парсим ID найденых вакансий
        for page in tqdm(range(total_pages), desc=f'Получение ID вакансий по должности: {job_title}'):
            response = self.search_vacancies(job_title, page=page)
            
            if response and 'items' in response:
                for item in response['items']:
                    vacancy_ids.append(item['id'])
        
        print(f'✅ Успех: ID вакансий {len(vacancy_ids)} для должности "{job_title}" спарсины')
        return vacancy_ids
    
    def get_vacancies_details(self, vacancy_ids: List[str]) -> List[Dict[str, Any]]:
        """Получение полной информации о списке вакансий
        Param:
            vacancy_ids: Список ID вакансий
        Returns:
            Информации о вакансиях"""
        vacancies_data = []
        
        for vac_id in tqdm(vacancy_ids, desc='Получение полной информации '):
            try:
                vacancy_data = self.get_vacancy_details(vac_id)
                if vacancy_data:
                    vacancies_data.append(vacancy_data)
            except Exception as e:
                print(f'❌ Ошибка: Обработка вакансиис ID {vac_id} вернуло ошибку: {e}')
        
        print(f'✅ Успех: Получено {len(vacancies_data)} вакансий')
        return vacancies_data
    
