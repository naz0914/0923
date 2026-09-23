"""
components/ai_advisor.py
AI 天氣顧問與生活決策模組 (對應教學步驟 22：延伸應用與想法)
根據氣象數據提供智慧穿搭、雨具提醒、戶外活動指標與 AI 播報稿
"""

from typing import Dict, Any


def generate_weather_advice(
    region_name: str,
    min_t: float,
    max_t: float,
    weather_condition: str,
    rain_prob: int,
) -> Dict[str, Any]:
    """
    根據氣象要素進行智慧生活決策分析
    """
    temp_diff = round(max_t - min_t, 1)

    # 1. 穿搭建議 (Clothing Advice)
    if max_t >= 32:
        clothing = "短袖、透氣排汗涼感衣物，戶外活動注意防曬與補充水分。"
        clothing_level = "炎熱防暑"
        clothing_color = "#E11D48"
    elif max_t >= 26:
        if temp_diff >= 6:
            clothing = f"白天舒適溫暖可著短袖，早晚溫差達 {temp_diff}°C，建議攜帶薄外套採洋蔥式穿法。"
        else:
            clothing = "著短袖或薄長袖棉質衣物，體感舒適宜人。"
        clothing_level = "舒適微溫"
        clothing_color = "#059669"
    elif max_t >= 20:
        clothing = "長袖上衣、針織衫或休閒風衣，體感偏涼。"
        clothing_level = "涼爽舒適"
        clothing_color = "#0284C7"
    else:
        clothing = "保暖毛衣、防風厚外套或羽絨衣，注意防寒保暖。"
        clothing_level = "偏冷防寒"
        clothing_color = "#6366F1"

    # 2. 雨具提醒 (Umbrella Advice)
    if rain_prob >= 70:
        umbrella = "降雨機率高，出門務必攜帶長傘或雨衣，提防短延時強降雨。"
        umbrella_badge = "🔴 必帶雨具"
    elif rain_prob >= 30:
        umbrella = "局部地區有短暫降雨機率，建議隨身攜帶折疊傘以備不時之需。"
        umbrella_badge = "🟡 建議備傘"
    else:
        umbrella = "降雨機率低，天氣大致穩定，外出不需特別帶傘。"
        umbrella_badge = "🟢 無需帶傘"

    # 3. 戶外活動與出遊指標 (Outdoor Index)
    if rain_prob <= 20 and 20 <= max_t <= 31:
        activity = "⭐⭐⭐⭐⭐ 天候極佳，非常適合戶外野餐、登山或各項休閒踏青！"
        activity_status = "極度適宜"
    elif rain_prob <= 40 and max_t < 34:
        activity = "⭐⭐⭐⭐ 天氣大致尚可，可進行戶外散步或輕度運動。"
        activity_status = "尚可適宜"
    elif rain_prob > 50:
        activity = "⭐⭐ 容易受降雨干擾，建議優先規劃室內藝文、閱讀或購物活動。"
        activity_status = "建議室內活動"
    else:
        activity = "⭐⭐⭐ 氣溫偏高炎熱，中午前後請盡量避免激烈戶外暴曬。"
        activity_status = "注意防曬補水"

    # 4. AI 天氣主播播報稿 (Broadcast Script)
    script = (
        f"早安！為您帶來【{region_name}】的即時氣象摘要。"
        f"今日預報為{weather_condition}，氣溫介於 {min_t} 到 {max_t} 度之間，"
        f"早晚溫差約 {temp_diff} 度。降雨機率為百分之 {rain_prob}。"
        f"{'出門記得攜帶雨具！' if rain_prob >= 30 else '整體天候穩定！'}"
        f"祝您今天擁有美好的一天！"
    )

    return {
        "clothing_advice": clothing,
        "clothing_level": clothing_level,
        "clothing_color": clothing_color,
        "umbrella_advice": umbrella,
        "umbrella_badge": umbrella_badge,
        "activity_advice": activity,
        "activity_status": activity_status,
        "broadcast_script": script,
        "temp_diff": temp_diff,
    }
