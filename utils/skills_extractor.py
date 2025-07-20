import re
from typing import List, Set, Dict
import pymorphy3  # Для морфологической нормализации

HARD_SKILLS = {
        # Языки программирования
        'python', 'java', 'javascript', 'js', 'typescript', 'c++', 'c#', 'php', 'go', 'rust', 'kotlin', 'swift','uml',
        'scala', 'r', 'matlab', 'perl', 'ruby', 'dart', 'elixir', 'haskell', 'clojure', 'f#', 'vb.net', 'draw', '1c', '1с',
        
        # Фреймворки и библиотеки
        'django', 'flask', 'fastapi', 'spring', 'react', 'vue', 'angular', 'node.js', 'express', 'laravel',
        'symfony', 'asp.net', 'rails', 'gin', 'echo', 'fiber', 'ktor', 'play', 'akka', 'spark',
        
        # Базы данных
        'postgresql', 'mysql', 'sqlite', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'neo4j',
        'oracle', 'sql server', 'mariadb', 'dynamodb', 'cosmos db', 'firebase', 'supabase','sql','clickhouse',
        
        # Облачные платформы
        'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'linode', 'vultr',
        
        # Инструменты разработки
        'git', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'bitbucket', 'jira', 'confluence',
        'slack', 'teams', 'trello', 'asana', 'notion', 'figma', 'sketch', 'adobe xd',
        
        # Методологии
        'agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'tdd', 'bdd', 'ddd',
        
        # Аналитика и ML
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'matplotlib', 'seaborn',
        'plotly', 'bokeh', 'jupyter', 'colab', 'spark', 'hadoop', 'kafka', 'airflow', 'dbt','dax',
        'tableau', 'power bi', 'looker', 'metabase', 'grafana', 'kibana', 'splunk', 'excel',
        'point','office', 'datalens','bi-системы', 'scipy','тесты',
        
        # Веб-технологии
        'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind', 'webpack', 'vite', 'babel',
        'jquery', 'lodash', 'axios', 'fetch', 'rest api', 'graphql', 'soap', 'grpc','xml',
        
        # Мобильная разработка
        'react native', 'flutter', 'xamarin', 'ionic', 'cordova', 'phonegap', 'swift ui',
        'kotlin android', 'java android', 'objective-c', 'cocoa',
        
        # Тестирование
        'selenium', 'cypress', 'playwright', 'puppeteer', 'jest', 'mocha', 'chai', 'pytest',
        'unittest', 'junit', 'testng', 'nunit', 'xunit', 'postman', 'insomnia',
        
        # Мониторинг и логирование
        'prometheus', 'datadog', 'new relic', 'sentry', 'logstash', 'fluentd', 'filebeat',
        'elasticsearch', 'logstash', 'kibana', 'elk stack',
        
        # Контейнеризация и оркестрация
        'docker', 'kubernetes', 'helm', 'rancher', 'openshift', 'nomad', 'consul', 'etcd',
        
        # Сети и безопасность
        'nginx', 'apache', 'traefik', 'istio', 'envoy', 'vault', 'keycloak', 'oauth','swagger',
        'jwt', 'ssl', 'tls', 'vpn', 'firewall', 'waf', 'ddos protection','api','json',
        
        # Другие инструменты
        'terraform', 'ansible', 'chef', 'puppet', 'salt', 'vagrant', 'virtualbox', 'vmware', 'etl','ui',
        'linux', 'ubuntu', 'centos', 'debian', 'red hat', 'suse', 'windows server','sap','битрикс',
        'macos', 'ios', 'android', 'unity', 'unreal engine', 'blender', 'maya', 'aris', 'epc', 'bpmn','erp'
    }
        
        # Список мягких навыков
SOFT_SKILLS = {
        'коммуникация': ['коммуникация', 'коммуникабельность', 'межличностные навыки', 
                        'навыки общения', 'общительность'],
        'лидерство': ['лидерство', 'лидерские качества', 'руководство'],
        'управление командой': ['управление командой', 'менеджмент', 'руководство группой'],
        'аналитическое мышление': ['аналитическое мышление', 'аналитические способности'],
        'креативность': ['креативность', 'творческий подход'],
        'адаптивность': ['адаптивность', 'гибкость', 'приспособляемость'],
        'ответственность': ['ответственность', 'обязательность'],
        'организованность': ['организованность', 'пунктуальность', 'дисциплинированность'],
        'работа в команде': ['работа в команде', 'командная работа', 'сотрудничество', 
                            'взаимопомощь', 'коллаборация'],
        'стрессоустойчивость': ['стрессоустойчивость', 'устойчивость к стрессу'],
        'проактивность': ['проактивность', 'инициативность', 'самостоятельность'],
        'тайм-менеджмент': ['тайм-менеджмент', 'управление временем'],
        'обучение': ['обучение', 'самообучение', 'обучаемость']
    }


class SkillsExtractor:

    def __init__(self):
        # Инициализация анализатора
        self.morph = pymorphy3.MorphAnalyzer()
        # Исходные навыки (сохраняем для отладки)
        self.raw_tech_skills = HARD_SKILLS  # текущий набор навыков
        self.raw_soft_skills = SOFT_SKILLS
        # Нормализованные навыки
        self.tech_skills = self.normalize_skills(self.raw_tech_skills)
        self.soft_skills = self.normalize_skills(self.raw_soft_skills)
        # Скомпилированные регулярные выражения
        self.hard_skills_pattern = self.build_skills_pattern(self.raw_tech_skills)
        self.soft_skills_pattern = self.build_skills_pattern(self.raw_soft_skills)

    def normalize_skills(self, skills: Set[str]) -> Dict[str, str]:
        """Нормализация навыков в начальную форму"""
        normalized = {}
        for skill in skills:
            # Приводим к начальной форме каждое слово в навыке
            words = []
            for word in skill.split():
                parsed = self.morph.parse(word)[0]
                words.append(parsed.normal_form)
            normalized[" ".join(words)] = skill
        return normalized

    def build_skills_pattern(self, skills: Set[str]) -> re.Pattern:
        """Создание регулярного выражения для поиска навыков"""
        escaped_skills = []
        for skill in skills:
            # Экранирование специальных символов
            escaped = re.escape(skill)
            # Поддержка разных написаний
            variants = [
                escaped,
                escaped.replace(r'\ ', r'[\s\-]?'),  # пробел/дефис
                escaped.replace(r'\ ', r'[^\w]?')     # любой разделитель
            ]
            escaped_skills.extend(variants)
        
        # Сортируем по длине (длинные навыки сначала)
        escaped_skills.sort(key=len, reverse=True)
        pattern = r'\b(' + '|'.join(escaped_skills) + r')\b'
        return re.compile(pattern, re.IGNORECASE)

    def clean_text(self, text: str) -> str:
        """Предобработка текста"""
        text = text.lower()
        text = re.sub(r'[^\w\s\-+]', ' ', text)  # Удаляем спецсимволы
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_skills_from_description(self, text: str, skills_type: str) -> List[str]:
            """Извлечение навыков из текста с учетом синонимов"""
            if not text or skills_type not in ('hard', 'soft'):
                return []
            
            # Приводим текст к нижнему регистру
            text_lower = text.lower()
            
            found_skills = []
            
            if skills_type == 'soft':
                # Ищем мягкие навыки по ключевым словам
                for skill, keywords in self.soft_skills.items():
                    for keyword in keywords:
                        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                            found_skills.append(skill)
                            break  # Не проверяем другие ключевые слова для этого навыка
            
            elif skills_type == 'hard':
                # Ищем технические навыки
                for skill in self.tech_skills:
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, text_lower):
                        found_skills.append(skill)
            
            # Удаляем дубликаты и возвращаем
            return sorted(list(set(found_skills))) 