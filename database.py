"""
database.py
SQLite 資料庫操作模組 (遵循課程步驟 8、9、10)
負責建立資料庫表、儲存氣溫預報資料及提供查詢介面
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Optional

DB_FILE = "data.db"


def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    """取得 SQLite 資料庫連線"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_FILE) -> None:
    """
    步驟 8 & 9：建立 SQLite 資料庫與 TemperatureForecasts 資料表
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS TemperatureForecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regionName TEXT NOT NULL,
                validDate TEXT NOT NULL,
                minT REAL,
                maxT REAL,
                weatherCondition TEXT,
                rainProbability INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(regionName, validDate) ON CONFLICT REPLACE
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_forecasts(data_list: List[Dict], db_path: str = DB_FILE) -> int:
    """
    將整理後的氣象預報資料寫入 SQLite 資料庫 (支援 UPSERT 避免重複)
    """
    init_db(db_path)
    conn = get_connection(db_path)
    sql = """
        INSERT INTO TemperatureForecasts (
            regionName, validDate, minT, maxT, weatherCondition, rainProbability, updated_at
        ) VALUES (
            :regionName, :validDate, :minT, :maxT, :weatherCondition, :rainProbability, CURRENT_TIMESTAMP
        );
    """
    try:
        cursor = conn.cursor()
        cursor.executemany(sql, data_list)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def get_all_regions(db_path: str = DB_FILE) -> List[str]:
    """
    步驟 10 範例：查詢所有縣市清單
    SELECT DISTINCT regionName FROM TemperatureForecasts;
    """
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts ORDER BY id ASC;")
        rows = cursor.fetchall()
        return [row["regionName"] for row in rows]
    finally:
        conn.close()


def get_forecast_by_region(region_name: str, db_path: str = DB_FILE) -> pd.DataFrame:
    """
    步驟 10 範例：查詢特定縣市的預報資料
    SELECT * FROM TemperatureForecasts WHERE regionName = ?;
    """
    init_db(db_path)
    conn = get_connection(db_path)
    query = """
        SELECT regionName, validDate, minT, maxT, weatherCondition, rainProbability, updated_at
        FROM TemperatureForecasts
        WHERE regionName = ?
        ORDER BY id ASC;
    """
    try:
        df = pd.read_sql_query(query, conn, params=(region_name,))
        return df
    finally:
        conn.close()


def get_all_forecasts(db_path: str = DB_FILE) -> pd.DataFrame:
    """
    查詢全台灣所有縣市的最新預報資料
    """
    init_db(db_path)
    conn = get_connection(db_path)
    query = """
        SELECT regionName, validDate, minT, maxT, weatherCondition, rainProbability, updated_at
        FROM TemperatureForecasts
        ORDER BY id ASC;
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("SQLite 資料庫初始化成功！資料表 TemperatureForecasts 已就緒。")
