"""
components/charts.py
氣溫趨勢圖表繪製模組 (對應教學步驟 14)
使用 Plotly 繪製互動式氣溫趨勢折線圖 (MaxT 與 MinT)
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Optional


def create_temperature_trend_chart(region_df: pd.DataFrame, region_name: str) -> go.Figure:
    """
    步驟 14：繪製最高溫與最低溫折線趨勢圖
    """
    if region_df.empty:
        fig = go.Figure()
        fig.update_layout(title="暫無該地區預報數據")
        return fig

    # 將 validDate 簡化為易讀的時間標籤 (例如：09/23 06:00~18:00)
    time_labels = []
    for d in region_df["validDate"]:
        parts = d.split("~")
        if len(parts) == 2:
            start_str = parts[0].strip()[5:16]  # MM-DD HH:MM
            end_str = parts[1].strip()[11:16]    # HH:MM
            time_labels.append(f"{start_str} ~ {end_str}")
        else:
            time_labels.append(d)

    fig = go.Figure()

    # 最高溫折線 (暖紅色)
    fig.add_trace(
        go.Scatter(
            x=time_labels,
            y=region_df["maxT"],
            mode="lines+markers+text",
            name="最高溫 (MaxT)",
            text=[f"{val}°C" for val in region_df["maxT"]],
            textposition="top center",
            line=dict(color="#FF6B6B", width=3, shape="spline"),
            marker=dict(size=9, color="#FF6B6B"),
            hovertemplate="<b>%{x}</b><br>最高溫: %{y}°C<extra></extra>",
        )
    )

    # 最低溫折線 (青藍色)
    fig.add_trace(
        go.Scatter(
            x=time_labels,
            y=region_df["minT"],
            mode="lines+markers+text",
            name="最低溫 (MinT)",
            text=[f"{val}°C" for val in region_df["minT"]],
            textposition="bottom center",
            line=dict(color="#4D96FF", width=3, shape="spline"),
            marker=dict(size=9, color="#4D96FF"),
            hovertemplate="<b>%{x}</b><br>最低溫: %{y}°C<extra></extra>",
        )
    )

    # 樣式與排版設定
    fig.update_layout(
        title={
            "text": f"📈 <b>{region_name}</b> 氣溫變化趨勢分析",
            "x": 0.05,
            "xanchor": "left",
            "font": {"size": 18, "color": "#2c3e50"},
        },
        xaxis=dict(
            title="預報時段",
            tickangle=-15,
            showgrid=True,
            gridcolor="#f0f2f5",
        ),
        yaxis=dict(
            title="溫度 (°C)",
            showgrid=True,
            gridcolor="#f0f2f5",
            range=[
                max(0, region_df["minT"].min() - 3),
                region_df["maxT"].max() + 3
            ],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified",
        height=360,
    )

    return fig
