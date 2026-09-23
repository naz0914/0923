"""
app.py
台灣天氣預報 Web 應用程式 (Taiwan Weather Forecast Dashboard)
對應教學步驟 11 ~ 20：
- 步驟 11: Streamlit 入門與版面排版
- 步驟 12: 從 SQLite 資料庫 (data.db) 讀取資料
- 步驟 13: 縣市下拉選單互動選擇 (Select Region)
- 步驟 14: 繪製最高與最低氣溫折線趨勢圖 (Plotly)
- 步驟 15: 顯示詳細預報數據表格
- 步驟 16: 整合現代化 Web App 介面 (指標卡片、氣象圖示)
- 步驟 17~19: Folium 台灣互動天氣地圖整合
- 步驟 20: 快取優化 (@st.cache_data) 與例外處理
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_folium import st_folium

# 引入本專案自訂模組
from database import init_db, get_all_regions, get_forecast_by_region, get_all_forecasts
from fetch_weather import update_weather_pipeline
from components.charts import create_temperature_trend_chart, create_multi_region_comparison_chart
from components.map_view import create_taiwan_weather_map
from components.ai_advisor import generate_weather_advice
from components.alerts import scan_weather_alerts

# 1. 頁面配置 (步驟 11 & 16)
st.set_page_config(
    page_title="台灣天氣預報儀表板 | CWA Weather Forecast",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 注入現代化自訂 CSS 樣式
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .badge-pop {
        display: inline-block;
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
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
        # 若資料庫無資料，自動觸發一次抓取
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
    st.image(
        "https://images.unsplash.com/photo-1592210454359-9043f067919b?w=500&auto=format&fit=crop&q=60",
        caption="CWA 氣象開放資料整合應用",
        use_container_width=True,
    )
    st.title("⚙️ 儀表板控制台")
    
    # 縣市選擇下拉選單
    default_index = regions.index("臺北市") if "臺北市" in regions else 0
    selected_region = st.selectbox(
        "📍 選擇縣市地區 (Select Region)：",
        options=regions,
        index=default_index,
        help="切換欲查看一週/多時段預報之縣市",
    )

    st.markdown("---")
    
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
        **💡 專案資訊**
        - 資料來源：中央氣象署 CWA API
        - 資料庫：SQLite (`data.db`)
        - 開發工具：Antigravity IDE × Gemini
        """
    )


# 主頁面頂部標題區
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    st.markdown('<div class="main-header">🌤️ 台灣天氣預報儀表板</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-header">即時觀測全台各縣市氣溫走勢、天氣現象與降雨機率 ｜ 目前關注地區：<b>{selected_region}</b></div>',
        unsafe_allow_html=True,
    )
with col_header2:
    if not all_forecasts_df.empty and "updated_at" in all_forecasts_df.columns:
        last_updated = all_forecasts_df["updated_at"].max()
        st.caption(f"🕒 資料庫更新時間：\n{last_updated}")

# 步驟 22 防災應用：掃描全台極端天氣警報
alerts = scan_weather_alerts(all_forecasts_df)
if alerts:
    with st.expander(f"⚠️ 全台即時氣候與防災預警提示 (共偵測到 {len(alerts)} 筆重點警示)", expanded=False):
        alert_cols = st.columns(min(3, len(alerts)))
        for idx, alt in enumerate(alerts[:3]):
            with alert_cols[idx]:
                st.markdown(
                    f"""
                    <div style="background:#FFF1F2; border-left:4px solid {alt['color']}; padding:10px 14px; border-radius:6px; margin-bottom:6px;">
                        <div style="font-weight:bold; color:#9F1239; font-size:0.92rem;">{alt['title']}</div>
                        <div style="font-size:0.83rem; color:#4C0519; margin-top:3px; line-height:1.4;">{alt['description']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# 取得選定縣市的預報資料
region_df = all_forecasts_df[all_forecasts_df["regionName"] == selected_region].reset_index(drop=True)

if not region_df.empty:
    latest_slot = region_df.iloc[0]

    # 步驟 16：頂部指標卡片 (Metric Cards)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">目前預報時段最高溫</div>
                <div class="metric-value" style="color: #E11D48;">{latest_slot['maxT']} °C</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">目前預報時段最低溫</div>
                <div class="metric-value" style="color: #2563EB;">{latest_slot['minT']} °C</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">預報天氣現象</div>
                <div class="metric-value" style="font-size: 1.4rem; color: #0F172A;">{latest_slot['weatherCondition']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">預測降雨機率</div>
                <div class="metric-value" style="color: #0284C7;">💧 {latest_slot['rainProbability']}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 頁籤分頁設計：兼顧圖表分析、互動地圖、AI生活顧問與數據明細 (步驟 14, 15, 17~19, 22)
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

        st.info("💡 **趨勢觀察提示**：折線呈現各時段最高與最低溫範圍，點擊或滑鼠懸停於節點可檢視詳細時段與精確溫度數值。")

        # 步驟 22 延伸應用：多縣市氣溫對比
        st.markdown("---")
        st.markdown("#### 🔄 跨縣市氣溫對比分析")
        st.caption("同時挑選多個縣市，比較不同地區最高氣溫變化走勢。")
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
        
        # 繪製 Folium 地圖 (步驟 17 & 18 & 19)
        folium_map = create_taiwan_weather_map(all_forecasts_df, selected_region=selected_region)
        st_folium(folium_map, width="100%", height=520, returned_objects=[])

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
                <div style="background:#f8fafc; border-left:4px solid {advice['clothing_color']}; padding:16px; border-radius:8px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <div style="font-weight:700; font-size:1.05rem; color:#1e293b;">👔 今日穿搭指南 · <span style="color:{advice['clothing_color']}">{advice['clothing_level']}</span></div>
                    <div style="margin-top:8px; color:#475569; font-size:0.95rem; line-height:1.5;">{advice['clothing_advice']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="background:#f8fafc; border-left:4px solid #0284c7; padding:16px; border-radius:8px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <div style="font-weight:700; font-size:1.05rem; color:#1e293b;">☂️ 雨具攜帶提醒 · <span>{advice['umbrella_badge']}</span></div>
                    <div style="margin-top:8px; color:#475569; font-size:0.95rem; line-height:1.5;">{advice['umbrella_advice']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
                <div style="background:#f8fafc; border-left:4px solid #10b981; padding:16px; border-radius:8px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <div style="font-weight:700; font-size:1.05rem; color:#1e293b;">🏃 戶外休閒適宜度 · <span style="color:#059669;">{advice['activity_status']}</span></div>
                    <div style="margin-top:8px; color:#475569; font-size:0.95rem; line-height:1.5;">{advice['activity_advice']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="background:#f1f5f9; border:1px solid #cbd5e1; padding:14px; border-radius:8px;">
                    <div style="font-weight:700; font-size:0.95rem; color:#334155; margin-bottom:6px;">🎙️ AI 天氣主播播報稿</div>
                    <div style="font-style:italic; color:#475569; font-size:0.92rem; line-height:1.6;">"{advice['broadcast_script']}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("##### 🌟 全台好天氣出遊排行榜 (低降雨機率精選 TOP 5)")
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
st.caption("Taiwan Weather Forecast Dashboard | Developed with Streamlit & Folium | AI x Coding Vibe Coding")
