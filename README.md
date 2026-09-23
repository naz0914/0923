# 🌤️ 台灣天氣預報儀表板 (Taiwan Weather Forecast Dashboard)

> **AI 創新微課程：從氣象資訊到 Web App**  
> 結合 **CWA Open Data API × Python × SQLite × Streamlit × Folium**，並透過 **Antigravity × Gemini** 實現 Vibe Coding 的現代化氣象數據儀表板。

---

## 📌 專案簡介 (Overview)

本專案為中央氣象署（CWA）開放資料串接與視覺化應用，從公開氣象 API 獲取全台各縣市一週氣溫預報，經過資料清洗與結構化處理後存入輕量型 SQLite 資料庫，最後以 Streamlit 打造具備互動折線圖與 Folium 台灣地圖的現代化氣象儀表板。

```
  [中央氣象署 CWA API]
           │ (requests / JSON)
           ▼
     [資料解析與清洗] (Pandas)
           │
           ▼
     [SQLite 資料庫] (data.db: TemperatureForecasts)
           │
           ▼
   [Streamlit 互動 Web 介面]
      ├── 縣市下拉選單切換
      ├── 一週氣溫趨勢折線圖 (MaxT / MinT)
      ├── 預報詳細數據表格
      └── Folium 互動式台灣氣象地圖
```

---

## 🛠️ 技術棧 (Tech Stack)

| 領域 | 工具 / 套件 | 說明 |
| :--- | :--- | :--- |
| **開發環境** | [Antigravity IDE](https://antigravity.google) | AI-first 整合開發環境 |
| **AI 協作模型** | Google Gemini | 自然語言輔助編程 (Vibe Coding) |
| **程式語言** | Python 3.10+ | 核心開發語言 |
| **資料來源** | [中央氣象署開放資料平台](https://opendata.cwa.gov.tw/) | 取得全台 36 小時 / 一週氣象預報 API |
| **資料處理** | Requests, Pandas | HTTP API 串接、JSON 解析與資料整理 |
| **資料儲存** | SQLite (`data.db`) | 輕量化關聯式資料庫，儲存結構化氣溫預報 |
| **Web 框架** | Streamlit | 快速建構互動式數據儀表板 |
| **資料視覺化** | Plotly / Altair, Folium | 氣溫趨勢折線圖、台灣地理圖資互動標記 |
| **版本控制** | Git & GitHub | 代碼版本管理與成果發布 |

---

## 🗄️ 資料庫設計 (Database Schema)

資料庫使用 SQLite，預設資料表為 `TemperatureForecasts`：

```sql
CREATE TABLE IF NOT EXISTS TemperatureForecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regionName TEXT NOT NULL,       -- 縣市名稱 (例: 臺北市、新北市、基隆市)
    validDate TEXT NOT NULL,        -- 預報日期/時間區間
    minT REAL,                      -- 最低溫度 (°C)
    maxT REAL,                      -- 最高溫度 (°C)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ✨ 核心功能 (Features)

1. **自動化 API 擷取與解析**：定時或按需向 CWA API 請求最新預報 JSON 資料，自動提取各縣市名稱、預報時間段與最高/最低溫（MaxT / MinT）。
2. **資料庫持久化**：使用 SQLite 記錄歷史與最新預報資料，避免頻繁請求 API，並支援自訂 SQL 查詢。
3. **互動式地區選擇**：提供全台 22 縣市下拉選單，即時切換目標觀測區域。
4. **一週氣溫趨勢圖**：動態繪製各縣市未來一週最高溫與最低溫變化趨勢圖。
5. **完整預報數據表**：表格化清晰陳列預報數值，支援下載或搜尋。
6. **台灣互動氣象地圖 (Folium)**：視覺化標註各地氣溫區間，一覽全台天氣概況。

---

## 🚀 快速開始 (Getting Started)

### 1. 取得中央氣象署 API Key
1. 前往 [中央氣象署氣象資料開放平台](https://opendata.cwa.gov.tw/)。
2. 註冊帳號並於「會員中心」取得個人專屬授權碼（API Authorization Code）。

### 2. 安裝相依套件
在專案目錄下執行以下指令：

```bash
pip install requests pandas streamlit folium streamlit-folium plotly
```

### 3. 環境變數設定
建立 `.env` 檔案或在程式碼中填入您的 CWA API Key：
```env
CWA_API_KEY=your_cwa_api_key_here
```

### 4. 執行資料擷取與啟動 Web App
```bash
# 1. 抓取氣象資料並存入 SQLite
python fetch_weather.py

# 2. 啟動 Streamlit 儀表板
streamlit run app.py
```

---

## 📂 專案架構規劃 (Project Structure)

```text
hw3 cwa/
├── .gitignore               # Git 忽略設定 (.env, __pycache__, 等)
├── README.md                # 專案說明文件
├── requirements.txt         # Python 依賴清單
├── fetch_weather.py         # CWA API 請求、JSON 解析與 SQLite 資料寫入模組
├── database.py              # SQLite 資料庫連線與查詢介面
├── app.py                   # Streamlit 主頁面與互動介面
├── data/
│   └── weather.db           # SQLite 本地資料庫檔案
└── components/
    ├── charts.py            # 折線圖繪製組件
    └── map_view.py          # Folium 地圖組件
```

---

## 🧭 Vibe Coding 開發旅程 (Antigravity × Gemini)

本專案遵循「打造你的 AI Coding Agent」之 10 步驟實踐：
- [x] **Step 1~3**：在 Antigravity 中開啟專案並規劃完整功能架構。
- [x] **Step 4~6**：建立 GitHub Repository 並透過 Git 與遠端完成連結。
- [x] **Step 7**：使用自然語言與 Gemini 對話，拆解步驟與撰寫規範 README。
- [ ] **Step 8**：實作 CWA API 模組、SQLite 資料庫與 Streamlit 介面。
- [ ] **Step 9**：加入地圖視覺化與圖表美化，持續除錯與優化效能。
- [ ] **Step 10**：提交所有代碼並推送到 GitHub 成果展示。

---

## 💡 未來延伸應用 (Future Roadmap)
- 📲 **LINE Bot 即時天氣提醒**：推播每日晨間降雨機率與出門建議穿著。
- 🗺️ **旅遊景點天氣推薦**：結合週末即時預報推薦晴天出遊縣市。
- 🚨 **極端天氣與防災預警**：低溫特報、大雨豪雨特報即時警示。
- 🤖 **生成式 AI 天氣主播**：結合 LLM 根據氣象數據自動生成自然語言天氣播報稿。
