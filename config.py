import os
from dotenv import dotenv_values

# Загрузка переменных окружения
env_vars = dotenv_values('.env')

#Настройки API
BASE_URL = 'https://api.hh.ru/vacancies'
USER_AGENT = env_vars.get('USER_AGENT', '')
PER_PAGE = 100

#Сохранение файлов
SAVE_CSV = True
SAVE_DB = True
SAVE_EXCEL = False

#Пути до файлов кэша
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENCY_CACHE_FILE = os.path.join(BASE_DIR, 'resources', 'currency_cache.json')
GEO_CACHE_FILE = os.path.join(BASE_DIR, 'resources', 'geo_cache.json')
DBNAME = os.path.join(BASE_DIR, 'resources', 'hh_sqllite.db')
CSV_FILE_PATH = os.path.join(BASE_DIR, 'resources', 'full_df.csv')
EXCEL_FILE_PATH = os.path.join(BASE_DIR, 'resources', 'full_df.xslx')


#Настройки парсинга
DEFAULT_TIME_DELAY = 0.4
DEFAULT_GEO_TIMEOUT = 10


#Список ролей
DEFAULT_VACANCIES = [
    'Аналитик данных',
    'Data Scientist',
    'BI аналитик',
    'Системный аналитик',
    'Дата-сайентист',
    'Бизнес-аналитик',
    'Продуктовый аналитик',
    'Data инженер'
]


# Исключения для валют
CURRENCY_EXCEPTIONS = {
    'BYR': 'BYN'
}


#Перевод зарплат в месячный эквивалент при размещении зарплата в час/год
SALARY_COEFFICIENTS = {
    'час': 160,
    'год': 1/12,
    'месяц': 1
}


#Ключевые слова для определения уровня, при необходимости изменить или расширить
GRADE_KEYWORDS = {
    'Intern': ['стажер', 'стажёр', 'интерн', 'помощник', 'intern', 'trainee'],
    'Junior': ['младший', 'junior', 'джуниор', 'начинающий'],
    'Middle': ['мидл', 'middle', 'средний', 'mid-level'],
    'Senior': ['сеньор', 'senior', 'старший', 'ведущий', 'опытный'],
    'Team Lead': ['тимлид', 'teamlead', 'руководитель', 'lead', 'главный']
}


# Настройки извлечения навыков из описания
EXTRACT_SKILLS_FROM_DESCRIPTION = True


# Показать статистику после завершения работы парсера
SHOW_STATS = True


IT_PROF_ROLES = [
    'Разработчик', 'Программист', 'Data Scientist', 'Аналитик данных', 'BI аналитик',
    'Системный аналитик', 'Дата-сайентист', 'Бизнес-аналитик', 'Продуктовый аналитик',
    'Data инженер', 'DevOps', 'QA', 'Тестировщик', 'Frontend', 'Backend', 'Fullstack',
    'ML Engineer', 'Системный администратор', 'Инженер по данным', 'Python', 'Java',
    'C++', 'C#', 'Go', 'Scala', 'JavaScript', 'TypeScript', 'PHP', 'Ruby', 'Android',
    'iOS', 'Mobile', 'AI', 'Machine Learning', 'Data Engineer', 'Data Analyst',
    'Software Engineer', 'Web-разработчик', 'Web developer', 'Game developer',
    'Unity', 'Unreal', '1C', 'SAP', 'Oracle', 'SQL', 'DWH', 'ETL', 'Big Data',
    'Cloud', 'Kubernetes', 'Docker', 'Network engineer', 'Security', 'Информационная безопасность'
]