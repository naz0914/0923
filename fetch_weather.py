"""
fetch_weather.py
中央氣象署 (CWA) 氣象資料擷取與處理模組
對應教學步驟：
- 步驟 4: 使用 Requests 取得 JSON 資料
- 步驟 5: JSON 資料結構解析
- 步驟 6: 提取最高溫、最低溫、天氣現象與降雨機率
- 步驟 7: 使用 Pandas 整理資料與預覽
- 步驟 8 & 9: 寫入 SQLite 資料庫 (data.db)
- 步驟 10: 執行 SQL 查詢驗證成果
"""

import os
import sys
import urllib3
import requests
import pandas as pd
from dotenv import load_dotenv

# 避免 Windows 終端機 (cp950) 輸出 UTF-8 / Emoji 編碼異常
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 引入自訂資料庫模組
from database import init_db, save_forecasts, get_all_regions, get_forecast_by_region

# 忽略不安全的 SSL 警告 (適應中央氣象署主機與 Python 3.14 憑證鏈檢查)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入 .env 環境變數
load_dotenv()

# 中央氣象署 API 金鑰 (優先讀取環境變數，若無則使用預設)
DEFAULT_API_KEY = "CWA-8C2E2368-812D-4F61-8F55-8AFC60837532"
API_KEY = os.getenv("CWA_API_KEY", DEFAULT_API_KEY).strip()

# 中央氣象署 今明 36 小時天氣預報 API 網址 (代號: F-C0032-001)
CWA_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"


def fetch_cwa_weather_json(api_key: str = API_KEY) -> dict:
    """
    步驟 4：使用 Requests 向中央氣象署 API 取得 JSON 資料
    """
    print("[INFO] 正在向中央氣象署請求天氣預報資料 (F-C0032-001)...")
    params = {
        "Authorization": api_key,
        "format": "JSON"
    }

    try:
        response = requests.get(CWA_API_URL, params=params, verify=False, timeout=15)
        response.raise_for_status()
        data = response.json()

        if not data.get("success") or "records" not in data:
            raise ValueError(f"API 回傳資料格式異常或授權失敗: {data}")

        print("[SUCCESS] 成功取得氣象原始 JSON 資料！")
        return data

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 網路請求失敗: {e}", file=sys.stderr)
        raise


def parse_weather_elements(raw_json: dict) -> pd.DataFrame:
    """
    步驟 5 & 6 & 7：
    - 解析 JSON 資料結構 (records -> location -> weatherElement)
    - 提取各縣市、時段、最高溫 (MaxT)、最低溫 (MinT)、天氣現象 (Wx)、降雨機率 (PoP)
    - 使用 Pandas 整理為乾淨的結構化 DataFrame
    """
    print("[INFO] 正在解析 JSON 資料結構並清洗數據...")
    locations = raw_json["records"]["location"]
    records_list = []

    for loc in locations:
        region_name = loc["locationName"]
        elements = loc["weatherElement"]

        # 將 weatherElement 依 elementName 建立字典對照
        element_dict = {elem["elementName"]: elem["time"] for elem in elements}

        # 各時段時間長度 (通常為 3 個時段)
        time_slots = len(element_dict.get("Wx", []))

        for idx in range(time_slots):
            # 取得該時段起訖時間
            time_info = element_dict["Wx"][idx]
            start_time = time_info["startTime"]
            end_time = time_info["endTime"]
            valid_date = f"{start_time} ~ {end_time}"

            # 提取天氣現象 (Wx)
            wx = element_dict.get("Wx", [])[idx]["parameter"]["parameterName"]

            # 提取降雨機率 (PoP)
            pop_str = element_dict.get("PoP", [])[idx]["parameter"]["parameterName"]
            pop = int(pop_str) if pop_str.isdigit() else 0

            # 提取最低溫 (MinT)
            mint_str = element_dict.get("MinT", [])[idx]["parameter"]["parameterName"]
            min_t = float(mint_str) if mint_str else None

            # 提取最高溫 (MaxT)
            maxt_str = element_dict.get("MaxT", [])[idx]["parameter"]["parameterName"]
            max_t = float(maxt_str) if maxt_str else None

            records_list.append({
                "regionName": region_name,
                "validDate": valid_date,
                "minT": min_t,
                "maxT": max_t,
                "weatherCondition": wx,
                "rainProbability": pop
            })

    # 轉為 Pandas DataFrame
    df = pd.DataFrame(records_list)
    print(f"[SUCCESS] 解析完成！共提取 {len(df)} 筆預報紀錄（涵蓋全台 {len(locations)} 個縣市）。")
    return df


def update_weather_pipeline():
    """
    整合完整資料處理流程：
    1. 取得 API 資料
    2. 解析與轉為 DataFrame
    3. 存入 SQLite 資料庫 (data.db)
    4. 驗證資料庫內容
    """
    # 1. 抓取資料
    raw_data = fetch_cwa_weather_json()

    # 2. 解析資料為 DataFrame (步驟 6 & 7)
    df = parse_weather_elements(raw_data)

    print("\n--- 【步驟 7：Pandas 資料預覽 (前 6 筆)】 ---")
    print(df.head(6).to_string(index=False))
    print("-" * 60)

    # 3. 寫入 SQLite 資料庫 (步驟 8 & 9)
    print("\n[INFO] 正在將資料寫入 SQLite 資料庫 (data.db)...")
    init_db()
    data_to_insert = df.to_dict(orient="records")
    saved_count = save_forecasts(data_to_insert)
    print(f"[SUCCESS] 成功寫入/更新 SQLite 資料表 `TemperatureForecasts`！(共處理 {len(data_to_insert)} 筆)")

    # 4. 執行 SQL 查詢測試 (步驟 10)
    print("\n--- 【步驟 10：SQL 查詢測試舉例】 ---")
    regions = get_all_regions()
    print(f"全台已有預報之縣市數量: {len(regions)}")
    print(f"縣市清單 (前 8 個): {', '.join(regions[:8])} ...")

    # 測試查詢基隆市或台北市
    target_region = "基隆市" if "基隆市" in regions else regions[0]
    print(f"\n查詢特定縣市 [{target_region}] 之預報紀錄：")
    sample_df = get_forecast_by_region(target_region)
    print(sample_df[["regionName", "validDate", "minT", "maxT", "weatherCondition", "rainProbability"]].to_string(index=False))

    return df


if __name__ == "__main__":
    update_weather_pipeline()
