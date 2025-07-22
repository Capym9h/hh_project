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
                    'навыки общения', 'общительность', 'устная коммуникация', 'письменная коммуникация'],
    'лидерство': ['лидерство', 'лидерские качества', 'руководство', 'наставничество', 'менторство'],
    'управление командой': ['управление командой', 'тимлид', 'менеджмент', 'руководство группой', 
                           'управление проектами', 'координация команды'],
    'аналитическое мышление': ['аналитическое мышление', 'аналитические способности', 
                              'критическое мышление', 'системное мышление', 'логическое мышление'],
    'креативность': ['креативность', 'творческий подход', 'инновационность', 
                    'нестандартное мышление', 'генерация идей'],
    'адаптивность': ['адаптивность', 'гибкость', 'приспособляемость', 
                    'работа в условиях неопределенности', 'реакция на изменения'],
    'эмоциональный интеллект': ['эмоциональный интеллект', 'эмпатия', 'понимание эмоций', 
                               'управление эмоциями', 'социальная чувствительность'],
    'решение проблем': ['решение проблем', 'проблемно-ориентированное мышление', 
                       'анализ проблем', 'поиск решений', 'устранение сложностей'],
    'работа в команде': ['работа в команде', 'командная работа', 'сотрудничество', 
                        'взаимопомощь', 'коллаборация', 'межфункциональное взаимодействие'],
    'стрессоустойчивость': ['стрессоустойчивость', 'устойчивость к стрессу', 
                           'работа под давлением', 'сохранение эффективности в стрессе'],
    'проактивность': ['проактивность', 'инициативность', 'самостоятельность', 
                     'предприимчивость', 'упреждающие действия'],
    'тайм-менеджмент': ['тайм-менеджмент', 'управление временем', 'организация времени', 
                       'расстановка приоритетов', 'планирование задач'],
    'обучение': ['обучение', 'самообучение', 'обучаемость', 'развитие навыков', 
                'непрерывное развитие', 'быстрое освоение нового'],
    'деловая этика': ['деловая этика', 'профессионализм', 'честность', 
                     'надежность', 'порядочность', 'ответственность'],
    'управление конфликтами': ['управление конфликтами', 'разрешение споров', 
                              'конструктивное решение конфликтов', 'медиация'],
    'клиентоориентированность': ['клиентоориентированность', 'фокус на клиенте', 
                                'понимание потребностей', 'сервисное мышление'],
    'переговоры': ['навыки переговоров', 'ведение переговоров', 'дипломатичность', 
                  'убеждение', 'аргументация'],
    'публичные выступления': ['публичные выступления', 'презентационные навыки', 
                             'доклады', 'спикинг'],
    'управление изменениями': ['управление изменениями', 'внедрение изменений', 
                              'адаптация к трансформациям', 'change management'],
    'мультикультурность': ['мультикультурность', 'работа в международной среде', 
                          'кросс-культурная коммуникация', 'глобальное мышление'],
    'этика ИИ': ['этика искусственного интеллекта', 'ответственное использование данных', 
                'этичные алгоритмы', 'AI ethics'],
    'цифровая грамотность': ['цифровая грамотность', 'технологическая адаптивность', 
                            'работа с цифровыми инструментами', 'digital literacy'],
    'устойчивость': ['устойчивость', 'резилиентность', 'способность к восстановлению', 
                    'преодоление трудностей'],
    'стратегическое планирование': ['стратегическое планирование', 'долгосрочное видение', 
                                   'построение стратегии', 'стратегическое мышление'],
    'управление рисками': ['управление рисками', 'идентификация рисков', 
                          'минимизация угроз', 'risk management'],
    'инклюзивность': ['инклюзивность', 'создание равных возможностей', 
                     'разнообразие и включение', 'diversity & inclusion']
}


class SkillsExtractor:

    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer()
        self.raw_tech_skills = HARD_SKILLS 
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
            escaped = re.escape(skill)
            variants = [
                escaped,
                escaped.replace(r'\ ', r'[\s\-]?'),
                escaped.replace(r'\ ', r'[^\w]?')
            ]
            escaped_skills.extend(variants)
        
        escaped_skills.sort(key=len, reverse=True)
        pattern = r'\b(' + '|'.join(escaped_skills) + r')\b'
        return re.compile(pattern, re.IGNORECASE)

    def clean_text(self, text: str) -> str:
        """Предобработка текста"""
        text = text.lower()
        text = re.sub(r'[^\w\s\-+]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_skills_from_description(self, text: str, skills_type: str) -> List[str]:
            """Извлечение навыков из текста с учетом синонимов"""
            if not text or skills_type not in ('hard', 'soft'):
                return []
            
            text_lower = text.lower()
            
            found_skills = []
            
            if skills_type == 'soft':
                for skill, keywords in self.soft_skills.items():
                    for keyword in keywords:
                        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                            found_skills.append(skill)
                            break
            
            elif skills_type == 'hard':
                for skill in self.tech_skills:
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, text_lower):
                        found_skills.append(skill)
            
            return sorted(list(set(found_skills))) 