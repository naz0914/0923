"""
build_stlite.py
自動建構適用於 Vercel (Stlite / WebAssembly) 的 index.html
將專案所有 Python 模組與組件打包為純前端單頁應用
"""

import os
import json


def build_stlite_html():
    files_to_pack = [
        "app.py",
        "database.py",
        "fetch_weather.py",
        "components/charts.py",
        "components/map_view.py",
        "components/ai_advisor.py",
        "components/alerts.py",
        ".streamlit/config.toml",
    ]

    virtual_fs = {}

    for file_path in files_to_pack:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                virtual_fs[file_path.replace("\\", "/")] = f.read()

    fs_json = json.dumps(virtual_fs, ensure_ascii=False)

    html_content = f"""<!doctype html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
  <title>台灣天氣預報儀表板 | CWA Weather Forecast (Vercel Edition)</title>
  <link rel="icon" href="https://fav.farm/🌤️" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.73.0/build/stlite.css" />
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #F8FAFC;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    #loading {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      color: #0F172A;
      text-align: center;
      padding: 20px;
    }}
    .spinner {{
      width: 52px;
      height: 52px;
      border: 5px solid #E2E8F0;
      border-top-color: #0284C7;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }}
    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}
    .tip-box {{
      margin-top: 18px;
      padding: 12px 20px;
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      color: #64748B;
      font-size: 13.5px;
      max-width: 440px;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <div id="loading">
    <div class="spinner"></div>
    <h2 style="margin: 20px 0 6px 0; font-size: 1.4rem; font-weight: 800; color: #0F172A;">
      🌤️ 正在啟動台灣天氣預報儀表板...
    </h2>
    <p style="color: #64748B; margin: 0; font-size: 0.95rem;">
      基於 WebAssembly (Wasm) 於瀏覽器端執行完整 Python & CWA 氣象引擎
    </p>
    <div class="tip-box">
      ✨ <b>Vercel Serverless Edge 版</b>：首次加載需下載 Pyodide 核心環境，請稍候約 5~10 秒。
    </div>
  </div>

  <div id="root"></div>

  <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.73.0/build/stlite.js"></script>
  <script>
    const files = {fs_json};

    stlite.mount({{
      requirements: [
        "pandas",
        "plotly",
        "folium",
        "streamlit-folium",
        "python-dotenv",
        "pyodide-http"
      ],
      entrypoint: "app.py",
      files: files
    }}, document.getElementById("root")).then(() => {{
      const loader = document.getElementById("loading");
      if (loader) {{
        loader.style.display = "none";
      }}
    }});
  </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("[SUCCESS] index.html successfully generated for Vercel deployment!")


if __name__ == "__main__":
    build_stlite_html()
