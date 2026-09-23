# 🌤️ 台灣天氣預報儀表板 (Taiwan Weather Forecast Dashboard)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-data.db-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Plotly](https://img.shields.io/badge/Plotly-7.1-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Folium](https://img.shields.io/badge/Folium-0.20-77B829?logo=leaflet&logoColor=white)](https://python-visualization.github.io/folium/)
[![AI-Powered](https://img.shields.io/badge/AI%20Coding-Antigravity%20%C3%97%20Gemini-6366F1)](https://antigravity.google)

> **AI 創新微課程：從氣象資訊到 Web App**  
> 結合 **中央氣象署 CWA Open Data API × Python × SQLite × Streamlit × Folium × Plotly**，並透過 **Antigravity × Gemini** 實現完整 Vibe Coding 的現代化旗艦氣象儀表板。

---

## 📌 專案簡介 (Overview)

本專案串接交通部中央氣象署（CWA）開放資料 API（`F-C0032-001` 全台今明 36 小時預報），經過資料清洗與結構化處理後持久化存儲於輕量級 SQLite 資料庫中。前端以 **Streamlit** 搭配自訂玻璃擬態（Glassmorphism）與微動效設計，打造整合**氣溫趨勢折線分析、跨縣市走勢對比、Folium 台灣互動地圖、極端氣候防災預警及 AI 生活決策顧問**之現代化氣象數據應用。

```
  [中央氣象署 CWA API (F-C0032-001)]
                  │ (requests / JSON)
                  ▼
       [資料解析與清洗 (Pandas)]
                  │ (sqlite3 upsert)
                  ▼
       [SQLite 資料庫 (data.db)]
                  │ (@st.cache_data)
                  ▼
   ┌───────────────────────────────────────────────┐
   │     Streamlit 現代玻璃擬態 Web 應用儀表板        │
   ├───────────────────────────────────────────────┤
   │  • ⚠️ 全台即時極端氣候與防災預警橫幅 (Alerts)    │
   │  • 🃏 頂部玻璃擬態氣象指標卡片 (Metric Cards)    │
   │  • 📈 氣溫變化走勢折線圖 (Plotly 漸層區間)       │
   │  • 🔄 跨縣市氣溫綜合對比分析 (Multi-region)      │
   │  • 🗺️ 全台 22 縣市互動氣溫地圖 (Folium)          │
   │  • 🤖 AI 智慧生活決策顧問 (穿搭/雨具/出遊/播報)  │
   │  • 📋 預報明細數據表格與一鍵匯出 CSV             │
   └───────────────────────────────────────────────┘
```

---

## 🛠️ 技術棧規格 (Tech Stack)

| 領域 | 工具 / 套件 | 說明 |
| :--- | :--- | :--- |
| **開發環境** | [Antigravity IDE](https://antigravity.google) | AI-first 整合開發環境 |
| **AI 協作模型** | Google Gemini (High) | 自然語言輔助編程與架構規劃 (Vibe Coding) |
| **程式語言** | Python 3.10+ / 3.14 | 核心後端開發語言 |
| **資料來源** | [中央氣象署氣象資料開放平台](https://opendata.cwa.gov.tw/) | 今明 36 小時天氣預報 API (`F-C0032-001`) |
| **資料處理** | Requests, Pandas, python-dotenv | HTTP API 串接、JSON 解析與 DataFrame 結構化 |
| **資料庫儲存** | SQLite (`data.db`) | 輕量化關聯式資料庫，支援 UPSERT 去重與防檔案鎖定保護 |
| **Web 框架** | Streamlit (1.64+) | 互動式 Web 數據應用框架 |
| **圖表視覺化** | Plotly (7.1+) | 現代字體、Spline 平滑曲線與溫差漸層色塊折線圖 |
| **地理圖資** | Folium & streamlit-folium | 全台 22 縣市中心座標標記、溫度漸層分級與彈跳卡片 |
| **樣式美學** | Vanilla CSS (Glassmorphism) | 引入 Google Fonts (Plus Jakarta Sans, Noto Sans TC) |
| **版本管理** | Git & GitHub | 代碼版本控制與自動化同步發布 |

---

## 🗄️ 資料庫設計 (Database Schema)

資料庫採用 SQLite（本地預設路徑 `data.db`），核心資料表為 `TemperatureForecasts`：

```sql
CREATE TABLE IF NOT EXISTS TemperatureForecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regionName TEXT NOT NULL,       -- 縣市名稱 (例: 臺北市、新北市、基隆市...)
    validDate TEXT NOT NULL,        -- 預報日期/時間區間 (例: 2026-09-23 06:00 ~ 18:00)
    minT REAL,                      -- 最低氣溫 (°C)
    maxT REAL,                      -- 最高氣溫 (°C)
    weatherCondition TEXT,          -- 天氣現象 (例: 晴時多雲、午後短暫陣雨...)
    rainProbability INTEGER,        -- 降雨機率 (%)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(regionName, validDate) ON CONFLICT REPLACE
);
```

> **關鍵優化**：透過 `UNIQUE(regionName, validDate) ON CONFLICT REPLACE` 機制，確保重抓資料時自動覆寫最新預報，避免累積歷史重複紀錄。

---

## ✨ 核心特色與功能模組 (Features)

### 1. 📡 自動化 API 擷取與清洗 (`fetch_weather.py`)
- 向中央氣象署請求全台 22 縣市最新預報 JSON 資料。
- 自動提取 `locationName`、`weatherElement`（最高溫 `MaxT`、最低溫 `MinT`、天氣現象 `Wx`、降雨機率 `PoP`）。
- 內建 Windows cp950 編碼相容與 Python 3.14 SSL 憑證保護機制。

### 2. 🃏 現代玻璃擬態儀表板 (`app.py`)
- **微光動態呼吸燈**：即時指示 API 連線健康度。
- **高質感指標卡片 (Metric Cards)**：具備頂部專屬色條（Top Accent Bar）、柔和氣泡圖標與滑鼠懸停微浮起動效（Hover Lift）。
- **側邊欄即時同步**：提供「🔄 立即從氣象署更新資料」按鈕，一鍵更新 SQLite 並清除 Streamlit 快取。

### 3. 📈 雙層溫差漸層折線圖 & 跨縣市對比 (`components/charts.py`)
- **單縣市走勢**：Plotly Spline 平滑折線，高低溫兩線之間填充微透光柔和色塊，一眼洞察日溫差。
- **跨縣市對比**：支援多選 2~5 個縣市，同張圖表即時對比不同地區氣溫走勢。

### 4. 🗺️ 台灣互動氣象地圖 (`components/map_view.py`)
- 整合台灣 22 縣市地理經緯度座標。
- 溫度分層設色標記（豔紅、琥珀金、翠綠、蔚藍、靛藍）。
- 點擊標記彈出圓角玻璃卡片，顯示天氣現象、氣溫區間與降雨機率。

### 5. 🤖 AI 智慧生活決策顧問 (`components/ai_advisor.py`)
- **👔 今日穿搭指南**：依據早晚溫差與高溫上限推薦洋蔥式穿法、透氣短袖或防寒衣物。
- **☂️ 雨具攜帶提醒**：降雨機率警戒機制（🔴 必帶雨具 / 🟡 建議備傘 / 🟢 無需帶傘）。
- **🏃 戶外活動指標**：五星級休閒適宜度評估。
- **🎙️ AI 天氣主播播報稿**：自然語言自動產出擬真播報短稿。
- **🌟 全台好天氣出遊排行榜**：自動篩選低降雨機率 TOP 5 出遊推薦縣市。

### 6. ⚠️ 極端氣候與防災預警提示 (`components/alerts.py`)
- 自動偵測高溫特報（≥ 33°C / ≥ 35°C）、強降雨警戒（≥ 60%）與劇烈溫差（≥ 8°C），於頂部以醒目警示橫幅提示。

### 7. 📥 預報數據一鍵匯出 CSV
- 表格分頁提供 UTF-8-sig 編碼匯出按鈕，保證 Windows Excel 開啟絕不亂碼。

---

## 📂 專案目錄結構 (Project Structure)

```text
hw3 cwa/
├── .env                     # 本地金鑰設定檔 (已透過 .gitignore 排除安全防外洩)
├── .env.example             # 金鑰範本供專案追蹤
├── .gitignore               # Git 忽略設定
├── .streamlit/
│   └── config.toml          # Streamlit 自訂主題與伺服器設置
├── requirements.txt         # Python 依賴套件清單
├── README.md                # 專案說明與規格文件
├── workflow.md              # 階段性開發流程與 Cheat Sheet
├── walkthrough.md           # 專案驗證報告與成果回顧
├── fetch_weather.py         # CWA API 請求、資料清洗與寫入 SQLite
├── database.py              # SQLite 資料庫操作與查詢介面
├── app.py                   # Streamlit 現代玻璃擬態主頁面
├── components/
│   ├── charts.py            # Plotly 折線圖與跨縣市對比組件
│   ├── map_view.py          # Folium 台灣互動地圖組件
│   ├── ai_advisor.py        # AI 生活決策顧問與播報稿組件
│   └── alerts.py            # 極端天氣與防災預警監控組件
└── tests/
    └── test_weather.py      # 自動化單元測試套件 (6 項測試 100% 通過)
```

---

## 🚀 快速開始 (Getting Started)

### 1. 取得中央氣象署 API Key
1. 前往 [中央氣象署氣象資料開放平台](https://opendata.cwa.gov.tw/) 註冊會員。
2. 於會員專區複製個人授權碼（Authorization Code）。

### 2. 安裝相依套件
在專案根目錄下執行：
```bash
pip install -r requirements.txt
```

### 3. 環境變數設定
在專案根目錄建立 `.env` 檔案並填入您的 API 金鑰：
```env
CWA_API_KEY=CWA-XXXXXXXXXXXXXXXXXXXXXXXX
```

### 4. 抓取氣象資料並存入資料庫
```bash
python fetch_weather.py
```

### 5. 啟動 Web 儀表板
```bash
python -m streamlit run app.py
```
啟動後於瀏覽器開啟：`http://localhost:8501` 即可體驗！

### 6. 執行自動化單元測試
```bash
python -m unittest tests/test_weather.py
```

---

## 🧭 Vibe Coding 開發歷程 (Antigravity × Gemini)

本專案依循「打造你的 AI Coding Agent」之 10 步驟實踐：
- [x] **Step 1~3**：在 Antigravity 中開啟專案，擬定 24 步開發架構規劃。
- [x] **Step 4~6**：建立 GitHub Repository 並透過 Git 與遠端建立關聯。
- [x] **Step 7**：使用自然語言與 Gemini 對話，拆解步驟並撰寫工作流程。
- [x] **Step 8**：實作 CWA API 模組、SQLite 資料庫與 Streamlit 基礎介面。
- [x] **Step 9**：加入 Folium 地圖、Plotly 趨勢折線圖、AI 生活決策顧問與現代玻璃擬態美學。
- [x] **Step 10**：通過完整單元測試，提交所有代碼並推送到 GitHub 正式發布。

---

## 🔗 相關連結 (Repository)
- **GitHub 專案儲存庫**：[https://github.com/naz0914/0923.git](https://github.com/naz0914/0923.git)
- **開發平台**：Google Antigravity IDE
