"""
components/alerts.py
極端天氣與防災預警監控模組 (對應教學步驟 22：農業與防災應用)
自動掃描全台縣市，偵測高溫警報、豪大雨警戒、低溫特報與劇烈溫差
"""

import pandas as pd
from typing import List, Dict, Any


def scan_weather_alerts(all_forecasts_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    掃描全台即時預報，產生各級災害與天氣預警
    """
    if all_forecasts_df.empty:
        return []

    # 取得各縣市第一筆最新預報
    latest_df = all_forecasts_df.groupby("regionName").first().reset_index()
    alerts = []

    # 1. 偵測高溫警報 (MaxT >= 33°C)
    high_temp_regions = latest_df[latest_df["maxT"] >= 33]
    for _, row in high_temp_regions.iterrows():
        level = "🔴 橙色高溫警報" if row["maxT"] >= 35 else "🟡 黃色高溫提示"
        alerts.append({
            "type": "heat",
            "level": level,
            "region": row["regionName"],
            "title": f"{level}：{row['regionName']} 最高溫達 {row['maxT']}°C",
            "description": "紫外線強烈，中午前後避免劇烈戶外活動，農作與戶外作業人員請加強防中暑措施。",
            "color": "#E11D48",
            "icon": "☀️",
        })

    # 2. 偵測強降雨機率警報 (PoP >= 60%)
    heavy_rain_regions = latest_df[latest_df["rainProbability"] >= 60]
    for _, row in heavy_rain_regions.iterrows():
        level = "🌧️ 降雨警戒" if row["rainProbability"] >= 80 else "💧 短暫強雨機率偏高"
        alerts.append({
            "type": "rain",
            "level": level,
            "region": row["regionName"],
            "title": f"{level}：{row['regionName']} 降雨機率達 {row['rainProbability']}%",
            "description": f"天氣現象預測為【{row['weatherCondition']}】，外出務必攜帶雨具，低窪地區留意排水與行車視線安全。",
            "color": "#0284C7",
            "icon": "🌧️",
        })

    # 3. 偵測劇烈日夜溫差 (MaxT - MinT >= 8°C)
    latest_df["temp_diff"] = latest_df["maxT"] - latest_df["minT"]
    large_diff_regions = latest_df[latest_df["temp_diff"] >= 8]
    for _, row in large_diff_regions.iterrows():
        alerts.append({
            "type": "diff",
            "level": "🌡️ 溫差警戒",
            "region": row["regionName"],
            "title": f"🌡️ 日夜溫差警示：{row['regionName']} 溫差達 {round(row['temp_diff'], 1)}°C",
            "description": f"最低溫 {row['minT']}°C，最高溫 {row['maxT']}°C，早晚溫差顯著，心血管疾病患者與長輩請留意適時添衣。",
            "color": "#D97706",
            "icon": "🧥",
        })

    return alerts
