import sqlite3
import pandas as pd
from typing import Optional, List, Literal
from config import DBNAME


class DatabaseHandler:
    """Класс для работы с базой данных SQLite"""

    def __init__(self, db_path: str = DBNAME):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """соединения с базой данных        
        Returns:
            Соединение с базой данных"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[List]:
        """Выполнение SQL запроса        
        Param:
            query: SQL запрос
            params: Параметры запроса
        Returns:
            Результат запроса или None"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchall()
                conn.commit()
                return result
        except Exception as e:
            print(f'Ошибка выполения запроса: {e}')
            print(f'Запрос: {query}')
            return None
    
    def create_vacancies_table(self) -> bool:
        """Создание таблицы для вакансий
        Returns:
            True если таблица создана успешно"""
        
        create_table_query = """
            CREATE TABLE IF NOT EXISTS full_sql
            (
                vac_id INTEGER PRIMARY KEY,
                vac_name TEXT,
                grade TEXT,
                city TEXT,
                geo TEXT,
                geo_city TEXT,
                published_at TEXT,
                archived INTEGER,
                employer_id INTEGER,
                emp_name TEXT,
                addres TEXT,
                is_accredited INTEGER,
                is_trusted INTEGER,
                salary_from INTEGER,
                salary_to INTEGER,
                currency TEXT,
                gross INTEGER,
                mode_name TEXT,
                frequency TEXT,
                prof_role TEXT,
                schedule_name TEXT,
                insider_interview INTEGER,
                response_letter_required INTEGER,
                experience TEXT,
                key_skills TEXT,
                has_test INTEGER,
                url TEXT,
                parsed_for_job TEXT
            )"""
        result = self.execute_query(create_table_query)
        return result is not None
    
    def save_dataframe_to_db(self, df: pd.DataFrame, table_name: str = 'full_df', 
                           if_exists: Literal['fail', 'replace', 'append'] = 'replace') -> bool:
        """Сохранение DataFrame в базу данных
        Args:
            df: DataFrame для сохранения
            table_name: Название таблицы
            if_exists: Действие если таблица существует ('fail', 'replace', 'append')
        Returns:
            True если сохранение прошло успешно"""
        try:
            with self._get_connection() as conn:
                df.to_sql(table_name, con=conn, if_exists=if_exists, index=False)
                return True
        except Exception as e:
            print(f'Ошибка: не удалось сохранить датафрейм в базуданных: {e}')
            return False
    
    def merge_tables(self, source_table: str = 'full_df', target_table: str = 'full_sql') -> bool:
        """Объединение таблиц (INSERT OR REPLACE)
        Args:
            source_table: Исходная таблица
            target_table: Целевая таблица
        Returns:
            True если объединение прошло успешно"""
        #информация о столбцах таблицы
        source_columns = self.execute_query(f"PRAGMA table_info({source_table})")
        target_columns = self.execute_query(f"PRAGMA table_info({target_table})")
        
        if not source_columns or not target_columns:
            print("Ошибка: Не удалось получить информацию")
            return False
        
        # Извлекаем названия столбцов
        source_col_names = [col[1] for col in source_columns]
        target_col_names = [col[1] for col in target_columns]
        
        # Находим общие столбцы
        common_columns = [col for col in source_col_names if col in target_col_names]
        
        if not common_columns:
            print("Ошибка: Нет совпадающих колонок")
            return False
        
        # Создаем запрос с явным указанием столбцов
        columns_str = ', '.join(common_columns)
        merge_query = f'''
        INSERT OR REPLACE INTO {target_table} ({columns_str})
        SELECT {columns_str} FROM {source_table}
        '''
        result = self.execute_query(merge_query)
        return result is not None
    
    def get_table_info(self, table_name: str) -> Optional[List]:
        """Получение информации о таблице
        Param:
            table_name: Название таблицы
        Returns:
            Информация о таблице"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def get_table_count(self, table_name: str) -> Optional[int]:
        """Получене числа записей
        Args:
            table_name: Название таблицы
        Returns:
            Количество записей"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.execute_query(query)
        return result[0][0] if result else None
    
    def load_dataframe_from_db(self, table_name: str = 'full_sql') -> Optional[pd.DataFrame]:
        """Загрузка DataFrame из базы данных
        Param:
            table_name: Название таблицы
        Returns:
            DataFrame с данными или None"""
        try:
            with self._get_connection() as conn:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                return df
        except Exception as e:
            print(f'Ошибка: Не удалось загрузить датафрейм из базыданных {e}')
            return None 