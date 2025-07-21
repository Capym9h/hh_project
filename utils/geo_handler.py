import os
import json
import pandas as pd
from typing import Dict, Optional
from geopy.geocoders import Nominatim
from config import GEO_CACHE_FILE, DEFAULT_GEO_TIMEOUT


class GeoHandler:
    """Класс для работы с геоданными"""
    
    def __init__(self, user_agent: str = "geoapi", timeout: int = DEFAULT_GEO_TIMEOUT):
        self.geolocator = Nominatim(user_agent=user_agent, timeout=timeout)
        self.cache_file = GEO_CACHE_FILE
        self.geo_cache: Dict[str, Optional[str]] = {}
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Загрузка кэша из файла"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.geo_cache = json.load(f)
            except Exception as e:
                print(f'❌ Ошибка: Загрузка файла ГЕОКЭШ не удалась: {e}')
                self.geo_cache = {}
        else:
            print('Внимание: Файл с ГЕО КЭШ не найден')
            with open(self.cache_file, 'w') as f:
                pass
            self.geo_cache = {}
    
    def _save_cache(self) -> None:
        """Сохранение кэша в файл"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.geo_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'Error saving geo cache: {e}')
    
    def get_city_geopoints(self, city: str) -> Optional[str]:
        """Получение координат центра города
        Args:
            city: Название города
        Returns:
            Строка с кординатами в формате [lat, lng] или None"""
        if not city or pd.isna(city):
            return None
        # Проверяем кэш
        if city in self.geo_cache and not (pd.isna(self.geo_cache.get(city))):
            return self.geo_cache[city]
        
        #получение гео точек города
        try:
            location = self.geolocator.geocode(f"{city}, Россия", exactly_one=True)
            if location:
                result = f'[{str(location.latitude)}, {str(location.longitude)}]'
            else:
                location = self.geolocator.geocode(f"{city}", exactly_one=True)
                if location:
                    result = f'[{str(location.latitude)}, {str(location.longitude)}]'
                else:
                    print(f'❌ Ошибка: Неудалось получить геоточки для: {city}')
                    result = None
        except Exception as e:
            print(f'❌ Ошибка: Запрос к geopy по городу {city} вернул ошибку: {e}')
            result = None
        
        if result:
            self.geo_cache[city] = result

        return result
    
    def save_cache(self) -> None:
        """Сохранение кэша в файл"""
        self._save_cache()
    
    def update_dataframe_geo(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обновление геоданных в DataFrame
        Param:
            df: DataFrame с данными
        Returns:
            DataFrame с обновленными геоданными"""
        if df.empty:
            return df
        
        # Создаем копию DataFrame
        df_copy = df.copy(deep=True)
        
        # Обновляем координаты
        for index, row in df_copy.iterrows():
            if pd.isna(row['geo']) or row['geo'] is None or row['geo'] == '':
                city = row['city']
                if city and not pd.isna(city):
                    geo_coords = self.get_city_geopoints(city)
                    if geo_coords:
                        df_copy.at[index, 'geo'] = geo_coords
        
        self.save_cache()
        return df_copy 