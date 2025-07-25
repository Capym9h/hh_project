import os
import time
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from tqdm import tqdm

from api.hh_api import HeadHunterAPI
from models.vacancy_parser import VacancyParser
from utils.currency_handler import CurrencyHandler
from utils.geo_handler import GeoHandler
from database.db_handler import DatabaseHandler
from config import SAVE_DB, SAVE_CSV, SAVE_EXCEL, SAVE_TO_DATALENS
from config import CSV_FILE_PATH, EXCEL_FILE_PATH, BASE_DIR, DATALENS_FILE_PATH
from config import DEFAULT_VACANCIES, DEFAULT_TIME_DELAY
from config import SHOW_STATS


class VacancyParserManager:
    
    def __init__(self, time_delay: float = 0.4):
        self.api = HeadHunterAPI() #класс для работы с АПИ ХХ
        self.api.set_time_delay(time_delay) #установка задержки отправки запросов
        self.geo_handler = GeoHandler() #класс для работы с гео данными
        self.parser = VacancyParser(self.geo_handler)  #класс для парсинга вакансий
        self.currency_handler = CurrencyHandler() #класс для обработка курса валют
        self.db_handler = DatabaseHandler() #класс для работы с базой данных
        
        self.all_vacancies_data = []
        self.current_job_title = None
    
    def parse_single_vacancy(self, job_id: str, job_title:str, max_pages: Optional[int] = None) -> pd.DataFrame:
        """Парсинг вакансий
        Args:
            job_id: ID профессии
            job_title: название профессии
            max_pages: Максимальное количество страниц (hh.api позволяет загружать до 20 страниц)
        Returns:
            DataFrame с данными вакансий"""
        
        print(f"\n{'='*50}")
        print(f"Начала парсинга вакансий по должности: {job_title}")
        print(f"{'='*50}")
        
        self.current_job_title = job_id
        
        #ID вакансий
        vacancy_ids = self.api.get_vacancy_ids(job_id, job_title, max_pages)
        
        if not vacancy_ids:
            print(f"Вакансии по должности '{job_title}' не найдены.")
            return pd.DataFrame()
        
        # Получаем полную информацию о вакансиях по их ID
        vacancies_data = self.api.get_vacancies_details(vacancy_ids)
        
        if not vacancies_data:
            print(f"Не удалось получить полную информацию о '{job_title}'")
            return pd.DataFrame()
        
        #парсим данные вакансий
        parsed_data = []
        for vacancy_data in tqdm(vacancies_data, desc=f'Парсинг вакансий по должности: "{job_title}"'):
            try:
                parsed_vacancy = self.parser.parse_vacancy(vacancy_data)
                parsed_data.append(parsed_vacancy)
                
            except Exception as e:
                print(f'❌ Ошибка: Не удалось спарсить {vacancy_data.get("id", "unknown")}: {e}')
        
        df = pd.DataFrame(parsed_data)
        
        if not df.empty:
            print(f"✅ Успех: Парсинг вакансий закончен. Получено {len(df)} вакансий по должности '{job_title}'")

            df['parsed_for_job'] = job_title
            
            self.all_vacancies_data.append(df)
        return df
    
    def parse_multiple_vacancies(self, job_titles: List[str], max_pages_per_job: Optional[int] = None) -> pd.DataFrame:
        """Парсинг вакансий для списка названий
        Args:
            job_titles: Список названий вакансий
            max_pages_per_job: Максимальное количество страниц для каждой вакансии
        Returns:
            Объединенный DataFrame со всеми данными"""
        print(f"\n{'='*60}")
        print(f"Начала парсинга для {len(job_titles)} должностей: ({', '.join(job_titles.keys())})")
        print(f"{'='*60}")
        
        self.all_vacancies_data = []
        
        for job_title, job_id in job_titles.items():
            df = self.parse_single_vacancy(job_id, job_title, max_pages_per_job)
            if not df.empty:
                self.all_vacancies_data.append(df)
        
        # Объединяем все данные
        if self.all_vacancies_data:
            combined_df = pd.concat(self.all_vacancies_data, ignore_index=True)
            
            for col in combined_df.columns:
                if combined_df[col].dtype == 'object':
                    combined_df[col] = combined_df[col].fillna('')
                    
                    combined_df[col] = combined_df[col].apply(
                        lambda x: str(x) if isinstance(x, (dict, list)) else x
                    )
            
            col_subset = [col for col in df.columns if col !='parsed_for_job']
            combined_df.drop_duplicates(subset=col_subset, inplace=True)

            print(f"\nВсего полученных вакансий: {len(combined_df)}")
            return combined_df
        else:
            print("❌ Ошибка: Парсинг не удался")
            return pd.DataFrame()
    
    def update_geo_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обновление геоданных в DataFrame
        Args:
            df: DataFrame с данными
        Returns:
            DataFrame с обновленными геоданными"""
        print("\nОбновление ГЕО данных...")
        
        #Если у вакансии не указаны ГЕО данные, добавляем их
        updated_df = self.geo_handler.update_dataframe_geo(df)
        
        print("✅ Успех: Геоданные обновлены")
        return updated_df
    
    def save_data(self, df: pd.DataFrame, 
                  save_csv: bool = SAVE_CSV, 
                  save_excel: bool = SAVE_EXCEL, 
                  save_db: bool = SAVE_DB,
                  save_to_datalens:bool = SAVE_TO_DATALENS) -> None:
        """Сохранение данных в различные форматы
        Args:
            df: DataFrame для сохранения
            save_csv: Сохранять в CSV 
            save_excel: Сохранять в Excel
            save_db: Сохранять в базу данных
            save_to_datalens: Сохраняем всю базу данных для импорта в DataLens, формат CSV"""
        if df.empty:
            print("Нет данных для сохранения")
            return
        
        print("\nСохранение данных...")
        
        #CSV
        if save_csv:
            try:
                # csv_path = 'resources/full_df.csv'
                df.to_csv(CSV_FILE_PATH, index=False)
                print(f"✅ Успех: CSV файл сохранен {CSV_FILE_PATH}")
            except Exception as e:
                print(f"❌ Ошибка: Не удалось сохранить CSV: {e}")
        
        #Excel
        if save_excel:
            try:
                # excel_path = f"'resources/my.xlsx"
                df.to_excel(EXCEL_FILE_PATH, index=False)
                print(f"✓ Excel файл сохранен {EXCEL_FILE_PATH}")
            except Exception as e:
                print(f"❌ Ошибка: Не удалось сохранить Excel: {e}")
        
        #DB
        if save_db:
            try:
                # Создаем таблицу если не существует
                self.db_handler.create_vacancies_table()
                
                # Сохраняем DataFrame в базу
                if self.db_handler.save_dataframe_to_db(df):
                    # Объединяем с основной таблицей
                    if self.db_handler.merge_tables():
                        print("✅ Успех: Данные сохранены в базу данных")
                    else:
                        print("❌ Ошибка: Не удалось объеденить таблицы в базеданных")
                else:
                    print("❌ Ошибка: Не удалось сохраниь базуданных")
            except Exception as e:
                print(f"❌ Ошибка: Возникла ошибка при работе с базой данных: {e}")
        
        #DataLens
        if save_to_datalens:
            try:
                datalens_db = self.db_handler.load_dataframe_from_db()
                datalens_db.to_csv(DATALENS_FILE_PATH, index=False)
                print(f"✅ Успех: Данные для DATALENS сохранены")
            except Exception as e:
                print(f"❌ Ошибка: Возникла ошибка при сохранения для DATALENS: {e}")

        print("✅ Успех: Данные сохранены")
    
    def convert_salaries_to_rub(self, df: pd.DataFrame) -> pd.DataFrame:
        """Конвертация всех зарплат в рубли        
        Args:
            df: DataFrame с данными
        Returns:
            DataFrame с зарплатами в рублях"""
        print("\nКонвертация зар.плат в рубли...")
        
        df_copy = df.copy(deep=True)
        
        #salary_from
        mask_from = (df_copy['salary_from'].notna()) & (df_copy['currency'].notna()) & (df_copy['currency'] != 'RUR')
        df_copy.loc[mask_from, 'salary_from'] = df_copy.loc[mask_from].apply(
            lambda row: self.currency_handler.convert_to_rub(row['salary_from'], row['currency']), axis=1
        )
        
        #salary_to
        mask_to = (df_copy['salary_to'].notna()) & (df_copy['currency'].notna()) & (df_copy['currency'] != 'RUR')
        df_copy.loc[mask_to, 'salary_to'] = df_copy.loc[mask_to].apply(
            lambda row: self.currency_handler.convert_to_rub(row['salary_to'], row['currency']), axis=1
        )
        
        # Обновляем валюту на рубли
        converted_mask = mask_from | mask_to
        df_copy.loc[converted_mask, 'currency'] = 'RUR'
        
        print(f"Переводена {converted_mask.sum()} зарплата в рубли")
        return df_copy
    
    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Получение статистики по данным
        Args:
            df: DataFrame с данными
        Returns:
            Словарь со статистикой"""
        if df.empty:
            return {}
        
        stats = {
            'total_vacancies_from_db':self.db_handler.get_table_count('full_sql'),
            'total_vacancies (by now)': len(df),
            'unique_jobs': df['parsed_for_job'].nunique() if 'parsed_for_job' in df.columns else 1,
            'cities_count': df['city'].nunique(),
            'employers_count': df['employer_id'].nunique(),
            'salary_stats': {
                'with_salary': len(df[df['salary_from'].notna() | df['salary_to'].notna()]),
                'avg_salary_from': df['salary_from'].mean() if 'salary_from' in df.columns else None,
                'avg_salary_to': df['salary_to'].mean() if 'salary_to' in df.columns else None,
            },
            'grade_distribution': df['grade'].value_counts().to_dict() if 'grade' in df.columns else {},
            'salary_distribution_by_grades':{
                'avg_salary_from': df.groupby(['grade']).salary_from.mean().round().to_dict(),
                'avg_salary_to': df.groupby(['grade']).salary_to.mean().round().to_dict()
            },
            'top_cities': df['city'].value_counts().head(10).to_dict() if 'city' in df.columns else {},
        }
        self.db_handler.close_conn()
        
        return stats
    
    def print_statistics(self, df: pd.DataFrame) -> None:
        """Вывод статистики в консоль
        Args:
            df: DataFrame с данными
        Returns: выводит статистику на экран"""
        stats = self.get_statistics(df)
        
        if not stats:
            print("Не удалось сделать статистику")
            return
        
        print("\n" + "="*50)
        print("Расчет статистики".upper())
        print("="*50)
        print(f"Всего вакансий в базе: {stats['total_vacancies_from_db']}")
        print(f"Всего вакансий за сеанс: {stats['total_vacancies (by now)']}")
        print(f"Всего должностей: {stats['unique_jobs']}")
        print(f"Города: {stats['cities_count']}")
        print(f"Уникальные работодатели: {stats['employers_count']}")
        
        if stats['salary_stats']['with_salary'] > 0:
            print(f"Вакансий с зар.платой: {stats['salary_stats']['with_salary']}")
            if stats['salary_stats']['avg_salary_from']:
                print(f"Средняя зар.плата (от): {stats['salary_stats']['avg_salary_from']:.0f} RUB")
            if stats['salary_stats']['avg_salary_to']:
                print(f"Средняя зар.плата (до): {stats['salary_stats']['avg_salary_to']:.0f} RUB")
        
        if stats['grade_distribution']:
            print("\nРаспределение grade:")
            for grade, count in stats['grade_distribution'].items():
                print(f"  {grade}: {count}")
        
        if stats['salary_distribution_by_grades']:
            print("\nРаспределение зар.платы по грейду:")
            for salary_type, grades in stats['salary_distribution_by_grades'].items():
                print(f"  {salary_type}")
                for grade, value in grades.items():
                    print(f"    {grade}: {value}")
        
        if stats['top_cities']:
            print("\nТоп 5 городов:")
            for city, count in list(stats['top_cities'].items())[:5]:
                print(f"  {city}: {count}")
        
        print("="*50)


def main():
    
    if not os.path.exists(os.path.join(BASE_DIR, 'resources')):
        os.mkdir(os.path.join(BASE_DIR,'resources'))

    parser_manager = VacancyParserManager(time_delay=DEFAULT_TIME_DELAY)
    job_titles = DEFAULT_VACANCIES
    
    #Старт парсера
    df = parser_manager.parse_multiple_vacancies(job_titles)
    
    if not df.empty:
        df = parser_manager.convert_salaries_to_rub(df)
        df = parser_manager.update_geo_data(df)

        #Вывод статистики
        if SHOW_STATS:
            parser_manager.print_statistics(df)

        parser_manager.save_data(df)
        print("\n✅ Успех: Парсинг закончен!")
    else:
        print("❌ Ошибка: Данные не найдены.")


if __name__ == "__main__":
    os.system('cls')
    time_start = time.time()
    main() 
    print('='*50)
    print(f'⌛ Время выполнения {(time.time()-time_start)//60 } минут')