"""
components/map_view.py
台灣氣象地圖視覺化模組 (對應教學步驟 17、18、19)
使用 Folium 繪製全台各縣市氣溫標記與互動地圖
"""

import folium
import pandas as pd
from typing import Optional

# 台灣 22 縣市中心地理座標 (緯度 Latitude, 經度 Longitude)
TAIWAN_COORDINATES = {
    "基隆市": (25.1276, 121.7392),
    "臺北市": (25.0330, 121.5654),
    "新北市": (25.0170, 121.4628),
    "桃園市": (24.9936, 121.3010),
    "新竹市": (24.8138, 120.9675),
    "新竹縣": (24.8387, 121.0177),
    "苗栗縣": (24.5602, 120.8214),
    "臺中市": (24.1477, 120.6736),
    "彰化縣": (24.0518, 120.5161),
    "南投縣": (23.9609, 120.9719),
    "雲林縣": (23.7092, 120.4313),
    "嘉義市": (23.4800, 120.4491),
    "嘉義縣": (23.4518, 120.2559),
    "臺南市": (22.9997, 120.2270),
    "高雄市": (22.6273, 120.3014),
    "屏東縣": (22.5519, 120.5487),
    "宜蘭縣": (24.7021, 121.7377),
    "花蓮縣": (23.9871, 121.6016),
    "臺東縣": (22.7583, 121.1444),
    "澎湖縣": (23.5711, 119.5793),
    "金門縣": (24.4493, 118.3766),
    "連江縣": (26.1505, 119.9499),
}


def get_temperature_color(max_t: Optional[float]) -> str:
    """依據最高溫決定地圖標記顏色 (視覺化漸層)"""
    if max_t is None:
        return "#7f8c8d"  # 灰色
    if max_t >= 32:
        return "#e74c3c"  # 炎熱紅色
    elif max_t >= 28:
        return "#e67e22"  # 溫暖橙色
    elif max_t >= 24:
        return "#f1c40f"  # 適中黃色
    elif max_t >= 20:
        return "#2ecc71"  # 舒適綠色
    else:
        return "#3498db"  # 涼冷藍色


def create_taiwan_weather_map(df: pd.DataFrame, selected_region: Optional[str] = None) -> folium.Map:
    """
    步驟 17 & 18 & 19：建立台灣互動氣象地圖
    - 取得各縣市的第一筆最新時段預報
    - 在對應座標加上標記點與氣溫資訊
    - 點擊標記可展開 Popup 詳細彈窗
    """
    # 地圖中心預設在台灣本島中央
    center_lat, center_lon = 23.8, 121.0
    
    # 若有選中特定縣市，將地圖中心微調至該縣市
    if selected_region and selected_region in TAIWAN_COORDINATES:
        center_lat, center_lon = TAIWAN_COORDINATES[selected_region]

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7 if not selected_region else 8,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # 取得每個縣市的第一筆（最新時段）預報
    latest_df = df.groupby("regionName").first().reset_index()

    for _, row in latest_df.iterrows():
        region = row["regionName"]
        if region not in TAIWAN_COORDINATES:
            continue

        lat, lon = TAIWAN_COORDINATES[region]
        min_t = row.get("minT", "N/A")
        max_t = row.get("maxT", "N/A")
        wx = row.get("weatherCondition", "未知")
        pop = row.get("rainProbability", 0)
        valid_date = row.get("validDate", "")

        is_selected = (region == selected_region)
        color = get_temperature_color(row.get("maxT"))

        # HTML Popup 彈跳卡片
        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 170px; line-height: 1.5;">
            <h4 style="margin: 0 0 6px 0; color: #2c3e50; border-bottom: 2px solid {color}; padding-bottom: 3px;">
                📍 {region}
            </h4>
            <div style="font-size: 13px; color: #555;">
                <p style="margin: 2px 0;"><b>天氣現象：</b>{wx}</p>
                <p style="margin: 2px 0;"><b>氣溫區間：</b><span style="color:#2980b9; font-weight:bold;">{min_t}°C</span> ~ <span style="color:#c0392b; font-weight:bold;">{max_t}°C</span></p>
                <p style="margin: 2px 0;"><b>降雨機率：</b>💧 {pop}%</p>
                <p style="margin: 4px 0 0 0; font-size: 11px; color: #888;">{valid_date.split('~')[0].strip()}</p>
            </div>
        </div>
        """

        # 圓形標記
        folium.CircleMarker(
            location=[lat, lon],
            radius=11 if is_selected else 7,
            color="#2c3e50" if is_selected else color,
            weight=3 if is_selected else 1.5,
            fill=True,
            fill_color=color,
            fill_opacity=0.9 if is_selected else 0.75,
            tooltip=f"{region}: {min_t}°C ~ {max_t}°C ({wx})",
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(m)

    return m
