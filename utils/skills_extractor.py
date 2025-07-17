import re
from typing import List, Set, Optional
from bs4 import BeautifulSoup


class SkillsExtractor:
    """Класс для извлечения навыков из описания вакансии"""
    
    def __init__(self):
        # Список популярных технологий и инструментов
        self.tech_skills = {
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
        self.soft_skills = {
            'коммуникация', 'коммуникабельность', 'лидерство', 'управление командой', 'менеджмент',
            'аналитическое мышление', 'креативность', 'проблемное мышление', 'критическое мышление',
            'адаптивность', 'гибкость', 'обучаемость', 'самообучение', 'саморазвитие',
            'ответственность', 'инициативность', 'проактивность', 'организованность',
            'внимание к деталям', 'точность', 'качество', 'производительность',
            'работа в команде', 'коллаборация', 'сотрудничество', 'взаимопомощь',
            'стрессоустойчивость', 'стрессоустойчивость', 'эмоциональный интеллект',
            'презентационные навыки', 'навыки презентации', 'публичные выступления',
            'навыки продаж', 'клиентоориентированность', 'customer focus',
            'проектное управление', 'project management', 'планирование', 'планирование проектов',
            'тайм-менеджмент', 'управление временем', 'приоритизация', 'делегирование',
            'наставничество', 'mentoring', 'коучинг', 'coaching', 'обучение', 'teaching'
        }
    
    def clean_text(self, text: str) -> str:
        """Очистка текста от HTML тегов и лишних символов"""
        if not text:
            return ""

        # Удаляем HTML теги
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Извлечение навыков из текста"""
        if not text:
            return []
        
        text = self.clean_text(text)
        found_skills = set()
        
        # Ищем технические навыки
        for skill in self.tech_skills:
            # Ищем точные совпадения (слова целиком)
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                found_skills.add(skill)
        
        # Ищем мягкие навыки
        for skill in self.soft_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                found_skills.add(skill)
        
        # Ищем навыки в кавычках или скобках
        quoted_pattern = r'["\']([^"\']*?)["\']'
        quoted_matches = re.findall(quoted_pattern, text)
        for match in quoted_matches:
            if len(match) > 2 and match.lower() in self.tech_skills:
                found_skills.add(match.lower())
        
        # Ищем навыки после ключевых слов
        skill_keywords = ['знание', 'опыт', 'навыки', 'умение', 'владение', 'знакомство']
        for keyword in skill_keywords:
            pattern = rf'{keyword}\s+([^,\.\s]+)'
            matches = re.findall(pattern, text)
            for match in matches:
                if match.lower() in self.tech_skills:
                    found_skills.add(match.lower())
        
        return sorted(list(found_skills))
    
    def extract_skills_from_description(self, description: Optional[str]) -> str:
        """Извлечение навыков из описания вакансии
        Args:
            description: Описание вакансии
        Returns:
            Строка с найденными навыками, разделенными точкой с запятой"""
        if not description:
            return ""
        
        skills = self.extract_skills_from_text(description)
        return '; '.join(skills) if skills else "" 