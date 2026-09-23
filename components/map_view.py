"""
components/map_view.py
台灣氣象地圖視覺化模組 (現代風格視覺化升級版)
使用 Folium 繪製具備現代色彩標記、發光圈與精美彈窗之全台天氣地圖
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
    """依據最高溫決定地圖標記現代漸層色 (Vibrant Modern Palette)"""
    if max_t is None:
        return "#94A3B8"
    if max_t >= 33:
        return "#F43F5E"  # 豔紅 (高溫警戒)
    elif max_t >= 28:
        return "#F59E0B"  # 琥珀金 (溫暖宜人)
    elif max_t >= 24:
        return "#10B981"  # 翠綠 (適溫舒適)
    elif max_t >= 20:
        return "#0EA5E9"  # 蔚藍 (清爽涼快)
    else:
        return "#6366F1"  # 靛藍 (偏冷防寒)


def create_taiwan_weather_map(df: pd.DataFrame, selected_region: Optional[str] = None) -> folium.Map:
    """
    步驟 17 & 18 & 19：建立現代風格台灣互動氣象地圖
    """
    center_lat, center_lon = 23.8, 121.0
    
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
        min_t = row.get("minT", "--")
        max_t = row.get("maxT", "--")
        wx = row.get("weatherCondition", "未知")
        pop = row.get("rainProbability", 0)
        valid_date = row.get("validDate", "")

        is_selected = (region == selected_region)
        color = get_temperature_color(row.get("maxT"))

        # 現代玻璃擬態 Popup 彈跳卡片
        popup_html = f"""
        <div style="font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; min-width: 190px; padding: 4px; line-height: 1.5;">
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid {color}; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="font-size: 16px; font-weight: 700; color: #0F172A;">📍 {region}</span>
                <span style="font-size: 11px; background: {color}20; color: {color}; padding: 2px 7px; border-radius: 12px; font-weight: 700;">{max_t}°C</span>
            </div>
            <div style="font-size: 13px; color: #334155;">
                <p style="margin: 3px 0;">🌤️ <b>預報天氣：</b>{wx}</p>
                <p style="margin: 3px 0;">🌡️ <b>溫差區間：</b><b style="color:#0284C7;">{min_t}°C</b> ~ <b style="color:#E11D48;">{max_t}°C</b></p>
                <p style="margin: 3px 0;">💧 <b>降雨機率：</b><b style="color:#0369A1;">{pop}%</b></p>
                <div style="margin-top: 8px; font-size: 11px; color: #94A3B8; border-top: 1px dashed #E2E8F0; padding-top: 4px;">
                    {valid_date.split('~')[0].strip() if '~' in valid_date else valid_date}
                </div>
            </div>
        </div>
        """

        # 現代圓形標記
        folium.CircleMarker(
            location=[lat, lon],
            radius=12 if is_selected else 8,
            color="#0F172A" if is_selected else "#FFFFFF",
            weight=3.5 if is_selected else 2,
            fill=True,
            fill_color=color,
            fill_opacity=0.92 if is_selected else 0.82,
            tooltip=f"<b>{region}</b>: {min_t}°C ~ {max_t}°C ({wx})",
            popup=folium.Popup(popup_html, max_width=320),
        ).add_to(m)

    return m
