"""
tests/test_weather.py
單元測試模組 (遵循教學步驟 20：程式品質與優化)
測試資料庫操作、AI 生活決策顧問、圖表與地圖生成邏輯
"""

import os
import gc
import unittest
import pandas as pd
from database import init_db, save_forecasts, get_all_regions, get_forecast_by_region
from components.ai_advisor import generate_weather_advice
from components.charts import create_temperature_trend_chart
from components.map_view import create_taiwan_weather_map

TEST_DB = "test_data.db"


class TestWeatherApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """測試類別啟動前建立測試庫"""
        cls.cleanup_db()
        init_db(TEST_DB)

    @classmethod
    def tearDownClass(cls):
        """測試類別完成後清理測試庫"""
        cls.cleanup_db()

    @classmethod
    def cleanup_db(cls):
        gc.collect()
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except PermissionError:
                pass

    def test_save_and_query_forecasts(self):
        """測試資料寫入與查詢機制"""
        mock_data = [
            {
                "regionName": "臺北市",
                "validDate": "2026-09-23 06:00:00 ~ 2026-09-23 18:00:00",
                "minT": 25.0,
                "maxT": 32.0,
                "weatherCondition": "晴時多雲",
                "rainProbability": 20,
            },
            {
                "regionName": "臺北市",
                "validDate": "2026-09-23 18:00:00 ~ 2026-09-24 06:00:00",
                "minT": 24.0,
                "maxT": 28.0,
                "weatherCondition": "多雲",
                "rainProbability": 10,
            },
        ]
        # 寫入
        save_forecasts(mock_data, db_path=TEST_DB)

        # 查詢縣市清單
        regions = get_all_regions(db_path=TEST_DB)
        self.assertIn("臺北市", regions)

        # 查詢特定縣市
        df = get_forecast_by_region("臺北市", db_path=TEST_DB)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["maxT"], 32.0)
        self.assertEqual(df.iloc[0]["weatherCondition"], "晴時多雲")

    def test_ai_advisor_logic(self):
        """測試 AI 生活決策顧問判斷邏輯"""
        advice = generate_weather_advice(
            region_name="臺中市",
            min_t=22.0,
            max_t=31.0,
            weather_condition="午後短暫陣雨",
            rain_prob=60,
        )
        self.assertEqual(advice["temp_diff"], 9.0)
        self.assertIn("建議備傘", advice["umbrella_badge"])
        self.assertIn("薄外套", advice["clothing_advice"])
        self.assertIn("臺中市", advice["broadcast_script"])

    def test_charts_generation(self):
        """測試 Plotly 氣溫折線圖生成"""
        df = pd.DataFrame(
            [
                {"validDate": "2026-09-23 06:00:00 ~ 2026-09-23 18:00:00", "minT": 24.0, "maxT": 30.0},
                {"validDate": "2026-09-23 18:00:00 ~ 2026-09-24 06:00:00", "minT": 22.0, "maxT": 26.0},
            ]
        )
        fig = create_temperature_trend_chart(df, "花蓮縣")
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)  # MaxT 與 MinT 兩條線

    def test_map_generation(self):
        """測試 Folium 台灣氣象地圖生成"""
        df = pd.DataFrame(
            [
                {"regionName": "臺北市", "minT": 24.0, "maxT": 31.0, "weatherCondition": "多雲", "rainProbability": 20, "validDate": "test"},
                {"regionName": "高雄市", "minT": 26.0, "maxT": 33.0, "weatherCondition": "晴天", "rainProbability": 10, "validDate": "test"},
            ]
        )
        m = create_taiwan_weather_map(df, selected_region="臺北市")
        self.assertIsNotNone(m)


if __name__ == "__main__":
    unittest.main()
