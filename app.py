"""
app.py
台灣天氣預報 Web 應用程式 (Taiwan Weather Forecast Dashboard)
現代美學旗艦版 (Modern Glassmorphic Visual Upgrade)
- 整合中央氣象署 CWA API (F-C0032-001)
- SQLite (data.db) 輕量資料庫快取
- 現代玻璃擬態 (Glassmorphic) 儀表板視覺
- Plotly 平滑漸層氣溫趨勢折線圖 & 跨縣市對比
- Folium 全台 22 縣市互動氣溫地圖
- AI 智慧生活決策顧問 (穿搭/雨具/出遊/播報)
- 全台即時極端氣候與防災預警提示
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_folium import st_folium

# 引入自訂模組
from database import init_db, get_all_regions, get_forecast_by_region, get_all_forecasts
from fetch_weather import update_weather_pipeline
from components.charts import create_temperature_trend_chart, create_multi_region_comparison_chart
from components.map_view import create_taiwan_weather_map
from components.ai_advisor import generate_weather_advice
from components.alerts import scan_weather_alerts

# 1. 頁面配置
st.set_page_config(
    page_title="Taiwan Weather Dashboard | 台灣即時氣象儀表板",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 注入頂級現代風格 CSS (Google Fonts + Glassmorphism + Micro-animations)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 隱藏預設 Streamlit 冗餘頂部間距 */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* 頂部 Hero 漸層標題區塊 */
    .hero-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(241, 245, 249, 0.7) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04), 0 8px 10px -6px rgba(15, 23, 42, 0.02);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
        padding: 4px 12px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 10px;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #22C55E;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0F172A 0%, #0369A1 50%, #4F46E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        margin: 0;
    }

    .hero-subtitle {
        font-size: 0.98rem;
        color: #64748B;
        margin-top: 6px;
        line-height: 1.5;
    }

    /* 現代玻璃擬態指標卡片 (Metric Cards) */
    .metric-card-modern {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.02);
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .metric-card-modern:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.03);
    }

    .card-top-accent {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }

    .metric-header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }

    .metric-label-clean {
        font-size: 0.82rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-icon-bubble {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }

    .metric-value-huge {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
    }

    .metric-desc {
        font-size: 0.82rem;
        color: #94A3B8;
        margin-top: 6px;
    }

    /* 氣象警報膠囊 */
    .alert-banner-box {
        background: #FFF1F2;
        border: 1px solid #FFE4E6;
        border-left: 5px solid #F43F5E;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 18px;
    }

    /* 側邊欄精緻按鈕與元件 */
    .stButton>button {
        background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 18px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #0369A1 0%, #1D4ED8 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=600)
def load_all_forecast_data() -> pd.DataFrame:
    """步驟 12 & 20：從 SQLite 資料庫讀取全部預報資料 (快取 10 分鐘)"""
    init_db()
    df = get_all_forecasts()
    if df.empty:
        update_weather_pipeline()
        df = get_all_forecasts()
    return df


@st.cache_data(ttl=600)
def load_regions_list() -> list:
    """步驟 10 & 13：取得縣市清單"""
    init_db()
    regions = get_all_regions()
    if not regions:
        update_weather_pipeline()
        regions = get_all_regions()
    return regions


# 載入資料
all_forecasts_df = load_all_forecast_data()
regions = load_regions_list()

# 側邊欄控制項 (步驟 13)
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 12px;">
            <div style="font-size: 2.6rem;">🌤️</div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A;">Taiwan Weather</div>
            <div style="font-size: 0.8rem; color: #64748B;">Central Weather Administration</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # 縣市選擇下拉選單
    default_index = regions.index("臺北市") if "臺北市" in regions else 0
    selected_region = st.selectbox(
        "📍 觀測目標縣市 (Select Region)：",
        options=regions,
        index=default_index,
        help="切換欲檢視之縣市氣象預報",
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # 一鍵更新按鈕
    st.subheader("🔄 氣象資料同步")
    if st.button("立即從氣象署更新資料", use_container_width=True):
        with st.spinner("正在向中央氣象署 API 請求最新數據並寫入資料庫..."):
            try:
                update_weather_pipeline()
                st.cache_data.clear()
                st.success("✅ 更新成功！")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 更新失敗: {e}")

    st.markdown("---")
    st.markdown(
        """
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px; font-size: 0.85rem; color: #475569;">
            <div style="font-weight: 700; color: #0F172A; margin-bottom: 4px;">🛠️ 技術棧規格</div>
            <div>• CWA API (F-C0032-001)</div>
            <div>• SQLite (data.db)</div>
            <div>• Streamlit & Plotly</div>
            <div>• Folium 地理圖資</div>
            <div>• Antigravity × Gemini</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# 主頁面頂部現代 Hero 標題區
last_updated = all_forecasts_df["updated_at"].max() if (not all_forecasts_df.empty and "updated_at" in all_forecasts_df.columns) else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown(
    f"""
    <div class="hero-container">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div class="hero-badge">
                <span class="pulse-dot"></span>
                <span>即時開放氣象資料連線中 · CWA Open Data</span>
            </div>
            <div style="font-size: 0.82rem; color: #64748B; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 4px 12px; border-radius: 20px;">
                🕒 資料庫同步時間：{last_updated}
            </div>
        </div>
        <h1 class="hero-title">台灣天氣預報儀表板</h1>
        <div class="hero-subtitle">
            全台 22 縣市即時氣候觀測、溫度區間走勢分析、Folium 地理圖資標註與 AI 生活決策顧問 ｜ 目前焦點：<b style="color: #0284C7; font-size: 1.05rem;">{selected_region}</b>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 步驟 22 防災應用：極端天氣警報提示
alerts = scan_weather_alerts(all_forecasts_df)
if alerts:
    with st.expander(f"⚠️ 全台即時氣候與防災預警提示 (共偵測到 {len(alerts)} 筆重點警示)", expanded=False):
        alert_cols = st.columns(min(3, len(alerts)))
        for idx, alt in enumerate(alerts[:3]):
            with alert_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background:#FFF1F2; border-left:4px solid {alt['color']}; padding:10px 14px; border-radius:8px; margin-bottom:6px;">
                        <div style="font-weight:700; color:#9F1239; font-size:0.92rem;">{alt['title']}</div>
                        <div style="font-size:0.83rem; color:#4C0519; margin-top:3px; line-height:1.4;">{alt['description']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# 取得選定縣市的預報資料
region_df = all_forecasts_df[all_forecasts_df["regionName"] == selected_region].reset_index(drop=True)

if not region_df.empty:
    latest_slot = region_df.iloc[0]

    # 步驟 16：頂部現代玻璃擬態指標卡片 (Metric Cards)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card-modern">
                <div class="card-top-accent" style="background: linear-gradient(90deg, #F43F5E, #FB7185);"></div>
                <div class="metric-header-row">
                    <span class="metric-label-clean">最高氣溫 (MaxT)</span>
                    <div class="metric-icon-bubble" style="background: #FFE4E6; color: #E11D48;">☀️</div>
                </div>
                <div class="metric-value-huge" style="color: #E11D48;">{latest_slot['maxT']} <span style="font-size: 1.2rem; font-weight: 600;">°C</span></div>
                <div class="metric-desc">預報時段極端高溫上限</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card-modern">
                <div class="card-top-accent" style="background: linear-gradient(90deg, #0EA5E9, #38BDF8);"></div>
                <div class="metric-header-row">
                    <span class="metric-label-clean">最低氣溫 (MinT)</span>
                    <div class="metric-icon-bubble" style="background: #E0F2FE; color: #0284C7;">❄️</div>
                </div>
                <div class="metric-value-huge" style="color: #0284C7;">{latest_slot['minT']} <span style="font-size: 1.2rem; font-weight: 600;">°C</span></div>
                <div class="metric-desc">預報時段晨間低溫下限</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card-modern">
                <div class="card-top-accent" style="background: linear-gradient(90deg, #F59E0B, #FBBF24);"></div>
                <div class="metric-header-row">
                    <span class="metric-label-clean">預報天氣現象</span>
                    <div class="metric-icon-bubble" style="background: #FEF3C7; color: #D97706;">🌤️</div>
                </div>
                <div class="metric-value-huge" style="font-size: 1.6rem; color: #0F172A; line-height: 1.4;">{latest_slot['weatherCondition']}</div>
                <div class="metric-desc">天空雲量與預報現象</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card-modern">
                <div class="card-top-accent" style="background: linear-gradient(90deg, #0284C7, #38BDF8);"></div>
                <div class="metric-header-row">
                    <span class="metric-label-clean">降雨機率 (PoP)</span>
                    <div class="metric-icon-bubble" style="background: #E0F2FE; color: #0369A1;">💧</div>
                </div>
                <div class="metric-value-huge" style="color: #0369A1;">{latest_slot['rainProbability']} <span style="font-size: 1.2rem; font-weight: 600;">%</span></div>
                <div class="metric-desc">降水機率指標</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 頁籤分頁設計 (步驟 14, 15, 17~19, 22)
    tab_chart, tab_map, tab_ai, tab_table = st.tabs([
        "📈 氣溫趨勢分析 (折線圖)",
        "🗺️ 台灣互動氣象地圖 (Folium)",
        "🤖 AI 智慧生活決策顧問",
        "📋 詳細預報資料表",
    ])

    with tab_chart:
        st.markdown(f"#### 📊 {selected_region} 未來時段氣溫預測走勢")
        chart_fig = create_temperature_trend_chart(region_df, selected_region)
        st.plotly_chart(chart_fig, use_container_width=True)

        st.info("💡 **趨勢觀察提示**：藍色與紅色節點分別為各時段低溫與高溫，陰影區塊呈現氣溫振幅範圍，滑鼠懸停於節點可檢視精確數值。")

        # 步驟 22 延伸應用：多縣市氣溫對比
        st.markdown("---")
        st.markdown("#### 🔄 跨縣市氣溫綜合對比分析")
        st.caption("挑選多個縣市，比較不同地區最高氣溫變化走勢。")
        default_compare = [selected_region] + [r for r in ["臺北市", "臺中市", "高雄市"] if r != selected_region][:2]
        compare_regions = st.multiselect(
            "選擇要比較的縣市清單 (可多選)：",
            options=regions,
            default=default_compare,
            key="multi_compare_select",
        )
        if compare_regions:
            comp_fig = create_multi_region_comparison_chart(all_forecasts_df, compare_regions)
            st.plotly_chart(comp_fig, use_container_width=True)

    with tab_map:
        st.markdown("#### 🗺️ 全台灣縣市即時氣溫地理分佈圖")
        st.caption("點擊地圖上的各縣市圓形氣溫標記，可展開該縣市的天氣現象與降雨機率卡片。")
        
        folium_map = create_taiwan_weather_map(all_forecasts_df, selected_region=selected_region)
        st_folium(folium_map, width="100%", height=530, returned_objects=[])

    with tab_ai:
        st.markdown(f"#### 🤖 {selected_region} AI 智慧生活決策顧問 (步驟 22 延伸應用)")
        st.caption("結合最新氣象要素，為您自動推算今日穿搭、雨具需求、戶外休閒建議與擬真主播摘要。")

        advice = generate_weather_advice(
            selected_region,
            float(latest_slot["minT"]),
            float(latest_slot["maxT"]),
            str(latest_slot["weatherCondition"]),
            int(latest_slot["rainProbability"]),
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid {advice['clothing_color']}; padding:18px; border-radius:12px; margin-bottom:14px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.03);">
                    <div style="font-weight:700; font-size:1.05rem; color:#0F172A;">👔 今日穿搭指南 · <span style="color:{advice['clothing_color']}; font-weight:800;">{advice['clothing_level']}</span></div>
                    <div style="margin-top:8px; color:#475569; font-size:0.95rem; line-height:1.6;">{advice['clothing_advice']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #0284c7; padding:18px; border-radius:12px; margin-bottom:14px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.03);">
                    <div style="font-weight:700; font-size:1.05rem; color:#0F172A;">☂️ 雨具攜帶提醒 · <span>{advice['umbrella_badge']}</span></div>
                    <div style="margin-top:8px; color:#475569; font-size:0.95rem; line-height:1.6;">{advice['umbrella_advice']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #10b981; padding:18px; border-radius:12px; margin-bottom:14px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.03);">
                    <div style="font-weight:700; font-size:1.05rem; color:#0F172A;">🏃 戶外休閒適宜度 · <span style="color:#059669; font-weight:800;">{advice['activity_status']}</span></div>
                    <div style="margin-top:8px; color:#475569; font-size:0.95rem; line-height:1.6;">{advice['activity_advice']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="background:linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); border:1px solid #CBD5E1; padding:16px; border-radius:12px;">
                    <div style="font-weight:700; font-size:0.95rem; color:#334155; margin-bottom:6px;">🎙️ AI 天氣主播播報稿</div>
                    <div style="font-style:italic; color:#475569; font-size:0.92rem; line-height:1.6;">"{advice['broadcast_script']}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("##### 🌟 全台好天氣出遊推薦榜 (低降雨機率精選 TOP 5)")
        latest_all = all_forecasts_df.groupby("regionName").first().reset_index()
        top_destinations = latest_all.sort_values(by=["rainProbability", "maxT"], ascending=[True, False]).head(5)

        top_cols = st.columns(len(top_destinations))
        for idx, (_, row) in enumerate(top_destinations.iterrows()):
            with top_cols[idx]:
                st.metric(
                    label=f"TOP {idx+1} {row['regionName']}",
                    value=f"{row['maxT']}°C",
                    delta=f"降雨率 {row['rainProbability']}%",
                    delta_color="inverse",
                )

    with tab_table:
        st.markdown(f"#### 📋 {selected_region} 預報明細數據表格 (步驟 15)")
        
        display_df = region_df.rename(
            columns={
                "regionName": "縣市名稱",
                "validDate": "預報有效時段",
                "minT": "最低溫 (°C)",
                "maxT": "最高溫 (°C)",
                "weatherCondition": "天氣現象",
                "rainProbability": "降雨機率 (%)",
                "updated_at": "記錄更新時間",
            }
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # 步驟 22 延伸應用：資料匯出下載
        csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label=f"📥 下載 {selected_region} 預報資料 (CSV)",
            data=csv_data,
            file_name=f"{selected_region}_weather_forecast.csv",
            mime="text/csv",
            help="匯出包含預報有效時段、氣溫、降雨機率與天氣現象之 CSV 表格 (UTF-8 編碼相容 Excel)",
        )

else:
    st.warning("⚠️ 尚無該地區之預報數據，請點擊左側「立即從氣象署更新資料」按鈕。")

# 頁尾
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94A3B8; font-size: 0.85rem; padding: 10px 0;">
        Taiwan Weather Forecast Dashboard | Built with Streamlit, Plotly & Folium | AI × Coding Vibe Coding
    </div>
    """,
    unsafe_allow_html=True,
)

# Vercel Serverless Python Runtime 相容導出 (避免 Vercel 尋找 app/handler 報錯)
def handler(request=None, *args, **kwargs):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain; charset=utf-8"},
        "body": "Taiwan Weather Forecast Dashboard is online. Frontend is served via index.html (Stlite Wasm).",
    }

app = handler
application = handler
