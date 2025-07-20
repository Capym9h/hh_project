import json
from typing import Dict, List, Optional, Any, Literal
from config import SALARY_COEFFICIENTS, GRADE_KEYWORDS, EXTRACT_SKILLS_FROM_DESCRIPTION
from utils.geo_handler import GeoHandler
from utils.skills_extractor import SkillsExtractor


class VacancyParser:
    """Класс для парсинга и обработки вакансий"""
    
    def __init__(self, geohandler):
        self.geohandler = geohandler
        self.skills_extractor = SkillsExtractor() if EXTRACT_SKILLS_FROM_DESCRIPTION else None
    
    def get_skills_string(self, key_skills: List[Dict[str, Any]], description: str, type_skills : Literal['hard','soft']='hard') -> str:
        """Преобразование списка словарей требуемых скилов в строку
        Param:
            key_skills: Список словарей с навыками
            type_skills: Показывает какие именно скилы мы парсим
        Returns:
            Строка с навыками"""
        if type_skills not in ('hard','soft'):
            return []

        if not key_skills and not description:
            return None
        
        result = []
        for skill in key_skills:
            skill_name = skill.get('name')
            if skill_name:
                result.append(skill_name)

        extracted_skills = self.skills_extractor.extract_skills_from_description(', '.join([description, *result]), type_skills) if self.skills_extractor else ""
        return '; '.join(extracted_skills)
        
    def _get_salary_coefficient(self, mode_name: str) -> float:
        """Получение коэффициента для перевода зарплаты (за час, за месяц, за год)
        Param:
            mode_name: Название периода оплаты
        Returns:
            Коэффициент для перевода"""
        
        mode_name = mode_name.replace('\xa0', ' ').lower()
        
        for period, coef in SALARY_COEFFICIENTS.items():
            if period in mode_name:
                return coef
        
        return 1.0  # По умолчанию за месяц
    
    def _determine_grade(self, vacancy_name: str) -> str:
        """Определение грейда вакансии
        Param:
            vacancy_name: Название вакансии
        Returns:
            Грейд вакансии"""
        
        name_lower = vacancy_name.lower()
        
        for grade, keywords in GRADE_KEYWORDS.items():
            if any(keyword in name_lower for keyword in keywords):
                return grade
        
        return 'Middle'
    
    def _process_salary(self, salary_data: Dict[str, Any], mode_data: Dict[str, Any]) -> tuple:
        """Обработка данных о зарплате
        Args:
            salary_data: Данные о зарплате
            mode_data: Данные о периоде оплаты
        Returns:
            Возвращает кортеж (salary_from, salary_to, currency, gross, mode_name)"""
        
        if not salary_data:
            return None, None, None, None, None
        
        #Обработка периода оплаты (за час, за месяц, за год)
        mode_name = mode_data.get('name', 'За месяц').replace('\xa0', ' ')
        coef = self._get_salary_coefficient(mode_name)
        
        #Обработка gross значений
        is_gross = salary_data.get('gross', True)
        conversion_rate = 0.87 if is_gross else 1.0
        
        raw_from = salary_data.get('from')
        raw_to = salary_data.get('to')
        
        salary_from = None
        salary_to = None
        
        if raw_from is not None:
            salary_from = raw_from * coef * conversion_rate
        
        if raw_to is not None:
            salary_to = raw_to * coef * conversion_rate
        
        currency = salary_data.get('currency')
        gross = salary_data.get('gross')
        
        return salary_from, salary_to, currency, gross, mode_data.get('name')
    
    def _process_address(self, address_data: Dict[str, Any], city_name:str) -> tuple:
        """Обработка данных об адресе        
        Param:
            address_data: Данные об адресе
            city: Название города
        Returns:
            Возвращает кортеж (address_raw, geo_coordinates)
        """
        if not address_data:
            # Если нет адреса, но есть город, получаем координаты города
            geo = self.geohandler.get_city_geopoints(city_name) if city_name else None
            return None, geo
        
        address_raw = address_data.get('raw')
        
        lat = address_data.get('lat')
        lng = address_data.get('lng')
        
        # Если есть координаты в вакансии, используем их
        if lat is not None and lng is not None:
            geo = f"[{lat}, {lng}]"
        else:
            # Иначе получаем координаты города
            geo = self.geohandler.get_city_geopoints(city_name)
        return address_raw, geo
    
    def parse_vacancy(self, vacancy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг данных вакансии
        Param:
            vacancy_data: Сырые данные вакансии из api HH
        Returns:
            Обработанные данные вакансии"""
        # Извлекаем основные данные
        employer = vacancy_data.get('employer', {})
        salary_range = vacancy_data.get('salary_range', {})
        mode = salary_range.get('mode', {}) if salary_range else {}
        prof_roles = vacancy_data.get('professional_roles', [])
        salary = vacancy_data.get('salary')
        address = vacancy_data.get('address')
        city_name = vacancy_data.get('area', {}).get('name')
        description = str(vacancy_data.get('description'))
        
        # Обработка зарплаты
        salary_from, salary_to, currency, gross, mode_name = self._process_salary(salary, mode)
        
        # Обработка адреса
        address_raw, geo = self._process_address(address, city_name)
        
        # Определение грейда
        grade = self._determine_grade(vacancy_data.get('name', ''))
        
        # Формирование результата
        result = {
            'vac_id': vacancy_data.get('id'),
            'vac_name': vacancy_data.get('name'),
            'grade': grade,
            'city': city_name,
            'geo': geo,
            'geo_city':self.geohandler.get_city_geopoints(city_name),
            'published_at': vacancy_data.get('published_at'),
            'archived': vacancy_data.get('archived'),
            'employer_id': employer.get('id'),
            'emp_name': vacancy_data.get('employment', {}).get('name'),
            'addres': address_raw,
            'is_accredited': employer.get('accredited_it_employer'),
            'is_trusted': employer.get('trusted'),
            'salary_from': salary_from,
            'salary_to': salary_to,
            'currency': currency,
            'gross': gross,
            'mode_name': mode_name,
            'frequency': mode.get('frequency'),
            'prof_role': prof_roles[0].get('name') if prof_roles else None,
            'schedule_name': vacancy_data.get('schedule', {}).get('name'),
            'insider_interview': vacancy_data.get('insider_interview'),
            'response_letter_required': vacancy_data.get('response_letter_required'),
            'experience': vacancy_data.get('experience', {}).get('name'),
            'hard_skills':self.get_skills_string(vacancy_data.get('key_skills', []), description),
            'soft_skills':self.get_skills_string(vacancy_data.get('key_skills', []), description, type_skills='soft'),
            'has_test': vacancy_data.get('has_test'),
            'url': vacancy_data.get('alternate_url')
        }
        return result