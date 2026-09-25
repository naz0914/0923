"""
database.py
SQLite 資料庫操作模組 (遵循課程步驟 8、9、10)
負責建立資料庫表、儲存氣溫預報資料及提供查詢介面
具備標準 SQLite3 與 Pyodide / WebAssembly (Wasm) 記憶體雙向備援相容機制
"""

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime

# 嘗試載入標準庫 sqlite3，若在 Pyodide / WebAssembly 無法使用則平滑降級為記憶體儲存
try:
    import sqlite3
    HAS_SQLITE = True
except ImportError:
    sqlite3 = None
    HAS_SQLITE = False

DB_FILE = "data.db"

# 記憶體降級儲存區 (用於 Pyodide / 無 sqlite3 環境)
_MEMORY_STORAGE = {}

# 預設 22 縣市初始資料 (確保在 Pyodide 離線/跨域受限時依然有完整展示數據)
INITIAL_WEATHER_DATA = [
    {"regionName": "臺北市", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 31.0, "weatherCondition": "晴時多雲", "rainProbability": 20},
    {"regionName": "臺北市", "validDate": "今晚 ~ 明日晨間", "minT": 23.0, "maxT": 27.0, "weatherCondition": "多雲", "rainProbability": 10},
    {"regionName": "臺北市", "validDate": "明日白天 ~ 明晚", "minT": 24.0, "maxT": 32.0, "weatherCondition": "午後短暫雷陣雨", "rainProbability": 40},
    {"regionName": "新北市", "validDate": "今日白天 ~ 今晚", "minT": 23.0, "maxT": 31.0, "weatherCondition": "晴時多雲", "rainProbability": 20},
    {"regionName": "新北市", "validDate": "今晚 ~ 明日晨間", "minT": 22.0, "maxT": 26.0, "weatherCondition": "多雲", "rainProbability": 10},
    {"regionName": "新北市", "validDate": "明日白天 ~ 明晚", "minT": 23.0, "maxT": 32.0, "weatherCondition": "午後短暫雷陣雨", "rainProbability": 40},
    {"regionName": "基隆市", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 29.0, "weatherCondition": "多雲時晴", "rainProbability": 20},
    {"regionName": "桃園市", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 32.0, "weatherCondition": "晴朗", "rainProbability": 10},
    {"regionName": "新竹市", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 31.0, "weatherCondition": "晴朗", "rainProbability": 10},
    {"regionName": "新竹縣", "validDate": "今日白天 ~ 今晚", "minT": 23.0, "maxT": 31.0, "weatherCondition": "晴朗", "rainProbability": 10},
    {"regionName": "苗栗縣", "validDate": "今日白天 ~ 今晚", "minT": 23.0, "maxT": 32.0, "weatherCondition": "晴時多雲", "rainProbability": 10},
    {"regionName": "臺中市", "validDate": "今日白天 ~ 今晚", "minT": 25.0, "maxT": 33.0, "weatherCondition": "晴時多雲", "rainProbability": 10},
    {"regionName": "彰化縣", "validDate": "今日白天 ~ 今晚", "minT": 25.0, "maxT": 33.0, "weatherCondition": "晴朗", "rainProbability": 10},
    {"regionName": "南投縣", "validDate": "今日白天 ~ 今晚", "minT": 23.0, "maxT": 32.0, "weatherCondition": "多雲午後陣雨", "rainProbability": 40},
    {"regionName": "雲林縣", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 33.0, "weatherCondition": "晴朗", "rainProbability": 10},
    {"regionName": "嘉義市", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 33.0, "weatherCondition": "晴時多雲", "rainProbability": 10},
    {"regionName": "嘉義縣", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 33.0, "weatherCondition": "晴時多雲", "rainProbability": 10},
    {"regionName": "臺南市", "validDate": "今日白天 ~ 今晚", "minT": 25.0, "maxT": 33.0, "weatherCondition": "晴時多雲", "rainProbability": 10},
    {"regionName": "高雄市", "validDate": "今日白天 ~ 今晚", "minT": 26.0, "maxT": 33.0, "weatherCondition": "晴時多雲", "rainProbability": 20},
    {"regionName": "屏東縣", "validDate": "今日白天 ~ 今晚", "minT": 25.0, "maxT": 34.0, "weatherCondition": "晴時多雲", "rainProbability": 20},
    {"regionName": "宜蘭縣", "validDate": "今日白天 ~ 今晚", "minT": 23.0, "maxT": 30.0, "weatherCondition": "多雲短暫雨", "rainProbability": 40},
    {"regionName": "花蓮縣", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 30.0, "weatherCondition": "多雲短暫陣雨", "rainProbability": 30},
    {"regionName": "臺東縣", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 31.0, "weatherCondition": "多雲短暫陣雨", "rainProbability": 30},
    {"regionName": "澎湖縣", "validDate": "今日白天 ~ 今晚", "minT": 25.0, "maxT": 31.0, "weatherCondition": "晴朗", "rainProbability": 10},
    {"regionName": "金門縣", "validDate": "今日白天 ~ 今晚", "minT": 24.0, "maxT": 30.0, "weatherCondition": "晴時多雲", "rainProbability": 10},
    {"regionName": "連江縣", "validDate": "今日白天 ~ 今晚", "minT": 22.0, "maxT": 28.0, "weatherCondition": "晴時多雲", "rainProbability": 10},
]


def get_connection(db_path: str = DB_FILE):
    """取得 SQLite 資料庫連線 (若無 sqlite3 則回傳 None)"""
    if not HAS_SQLITE:
        return None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_FILE) -> None:
    """
    步驟 8 & 9：建立 SQLite 資料庫與 TemperatureForecasts 資料表
    在 Pyodide 環境下初始化記憶體資料庫
    """
    if not HAS_SQLITE:
        if not _MEMORY_STORAGE:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for r in INITIAL_WEATHER_DATA:
                item = dict(r)
                item["updated_at"] = now_str
                key = (item["regionName"], item["validDate"])
                _MEMORY_STORAGE[key] = item
        return

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
    將整理後的氣象預報資料寫入資料庫 (支援 UPSERT 避免重複)
    """
    init_db(db_path)
    if not HAS_SQLITE:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for item in data_list:
            row = dict(item)
            row["updated_at"] = now_str
            key = (row["regionName"], row["validDate"])
            _MEMORY_STORAGE[key] = row
        return len(data_list)

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
    if not HAS_SQLITE:
        regions = []
        for k in _MEMORY_STORAGE.keys():
            if k[0] not in regions:
                regions.append(k[0])
        return regions

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
    if not HAS_SQLITE:
        rows = [v for k, v in _MEMORY_STORAGE.items() if k[0] == region_name]
        if not rows:
            return pd.DataFrame(columns=["regionName", "validDate", "minT", "maxT", "weatherCondition", "rainProbability", "updated_at"])
        return pd.DataFrame(rows)

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
    if not HAS_SQLITE:
        rows = list(_MEMORY_STORAGE.values())
        if not rows:
            return pd.DataFrame(columns=["regionName", "validDate", "minT", "maxT", "weatherCondition", "rainProbability", "updated_at"])
        return pd.DataFrame(rows)

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
    status = "SQLite3 引擎" if HAS_SQLITE else "Pyodide 記憶體備援引擎"
    print(f"資料庫模組初始化成功！運行模式：{status}。")
