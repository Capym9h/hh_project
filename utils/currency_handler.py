import os
import json
import requests
from typing import Dict, Optional
from config import CURRENCY_CACHE_FILE, CURRENCY_EXCEPTIONS


class CurrencyHandler:
    """Класс для работы с валютами и курсами валют"""
    
    def __init__(self):
        self.cache_file = CURRENCY_CACHE_FILE
        self.currency_cache = {}
        self.updated_currency = False
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Загрузка кэша валют из файла"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.currency_cache = json.load(f)
            except Exception as e:
                print(f'❌ Ошибка: Загрузка файла кэша валют закончилось неудачей, ошибка: {e}')
                self.currency_cache = {}
    
    def _save_cache(self) -> None:
        """Сохранение кэша валют в файл"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.currency_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'❌ Ошибка: Не удалось сохранить курс валют в файл кэша: {e}')
    
    def _update_currency_rates(self) -> None:
        """Обновление курсов валют спомощью GET запроса к ЦБ РФ"""
        if self.updated_currency:
            return

        try:
            response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=3)
            response.raise_for_status()
            data = response.json()
            currencies = data.get('Valute', {})
            
            for code, currency_data in currencies.items():
                nominal = currency_data.get('Nominal', 1)
                value = currency_data.get('Value')
                if nominal and value:
                    self.currency_cache[code] = value / nominal
            
            self._save_cache()
            self.updated_currency = True
            
        except Exception as e:
            print(f'❌ Ошибка: Не удалось обновить курсы валют: {e}')
    
    def get_currency_rate(self, currency: str) -> float:
        """Получение курса валюты
        Param:
            currency: Код валюты
        Returns:
            Курс валюты к рублю"""
        currency = currency.upper()
        
        #если есть исключения обрабатываем (см config.py)
        if currency in CURRENCY_EXCEPTIONS:
            currency = CURRENCY_EXCEPTIONS[currency]
        
        if not self.updated_currency:
            self._update_currency_rates()
        
        if currency in self.currency_cache:
            return self.currency_cache[currency]
        
        print(f'Внимание: Курс валюты "{currency}" не найден.')
        return 1.0
    
    def convert_to_rub(self, amount: float, currency: str) -> float:
        """Конвертация зарплаты из вакансии в рубли
        Param:
            amount: Сумма в исходной валюте
            currency: Код валюты
        Returns:
            Сумма в рублях"""
        if currency == 'RUR':
            return amount
        
        rate = self.get_currency_rate(currency)
        return round(amount * rate) 