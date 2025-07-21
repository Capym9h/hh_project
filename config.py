import os
from dotenv import dotenv_values

env_vars = dotenv_values('.env')

#Настройки API
BASE_URL = 'https://api.hh.ru/vacancies'
USER_AGENT = env_vars.get('USER_AGENT', '')
PER_PAGE = 100

#Сохранение файлов
SAVE_CSV = True
SAVE_DB = True
SAVE_EXCEL = False
SAVE_TO_DATALENS = True

#Пути до файлов кэша
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DBNAME = os.path.join(BASE_DIR, 'resources', 'hh_sqllite.db')
CURRENCY_CACHE_FILE = os.path.join(BASE_DIR, 'resources', 'currency_cache.json')
GEO_CACHE_FILE = os.path.join(BASE_DIR, 'resources', 'geo_cache.json')
CSV_FILE_PATH = os.path.join(BASE_DIR, 'resources', 'full_df.csv')
EXCEL_FILE_PATH = os.path.join(BASE_DIR, 'resources', 'full_df.xslx')
DATALENS_FILE_PATH = os.path.join(BASE_DIR, 'resources', 'to_DataLens.csv')


#Настройки парсера
DEFAULT_TIME_DELAY = 0.4 #задержка отправки запросов на hh.api
DEFAULT_GEO_TIMEOUT = 10 #задержка отправки запросов на geopy


#Список ролей
#найти другие роли и их цифровые коды можно сделав GET запрос на адрес: https://api.hh.ru/professional_roles
DEFAULT_VACANCIES = {
  "BI-аналитик, аналитик данных": "156",
  "Аналитик": "10",
  "Бизнес-аналитик": "150",
  "Дата-сайентист": "165",
  "Продуктовый аналитик": "164",
  "Руководитель отдела аналитики": "157",
  "Сетевой инженер": "112",
  "Системный аналитик": "148",
  "Системный инженер": "114"
}

# Исключения для валют
CURRENCY_EXCEPTIONS = {
    'BYR': 'BYN'
}

#Перевод зарплат в месячный эквивалент при размещении зарплата в час/год, за смену
SALARY_COEFFICIENTS = {
    'час': 160,
    'год': 1/12,
    'месяц': 1,
    'смену': 24
}

#Ключевые слова для определения уровня, при необходимости изменить или расширить
GRADE_KEYWORDS = {
    'Intern': ['стажер', 'стажёр', 'интерн', 'помощник', 'intern', 'trainee'],
    'Junior': ['младший', 'junior', 'джуниор', 'начинающий'],
    'Middle': ['мидл', 'middle', 'средний', 'mid-level'],
    'Senior': ['сеньор', 'senior', 'старший', 'ведущий', 'опытный'],
    'Team Lead': ['тимлид', 'teamlead', 'руководитель', 'lead', 'главный', 'начальник']
}


#экстракция скилов происходит из описания вакансии. Ключевые слова можно найти по пути unils/skill_extractor.py (HARD_SKILLS, SOFT_SKILLS). При необходимости расширить или изменить
# Настройки извлечения навыков из описания
EXTRACT_SKILLS_FROM_DESCRIPTION = True

#Вывести статистику после завершения парсинга?
SHOW_STATS = True