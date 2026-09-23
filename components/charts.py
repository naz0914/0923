"""
components/charts.py
氣溫趨勢圖表繪製模組 (現代風格視覺化升級版)
使用 Plotly 繪製具備漸層填充、平滑微光折線與現代字體之圖表
"""

import pandas as pd
import plotly.graph_objects as go
from typing import List


MODERN_FONT = "'Plus Jakarta Sans', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif"


def create_temperature_trend_chart(region_df: pd.DataFrame, region_name: str) -> go.Figure:
    """
    繪製現代風格最高溫與最低溫折線趨勢圖 (含溫差區間透光漸層)
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

    # 最低溫折線 (青藍色底層線)
    fig.add_trace(
        go.Scatter(
            x=time_labels,
            y=region_df["minT"],
            mode="lines+markers+text",
            name="最低溫 (MinT)",
            text=[f"<b>{val}°C</b>" for val in region_df["minT"]],
            textposition="bottom center",
            textfont=dict(family=MODERN_FONT, size=12, color="#0284C7"),
            line=dict(color="#0EA5E9", width=3, shape="spline"),
            marker=dict(
                size=10,
                color="#0EA5E9",
                line=dict(color="#FFFFFF", width=2.5),
            ),
            hovertemplate="<b>%{x}</b><br>最低溫: <span style='color:#0EA5E9;font-weight:bold;'>%{y}°C</span><extra></extra>",
        )
    )

    # 最高溫折線 (暖紅亮橙色，並在兩線之間填充柔和藍紫漸層色塊)
    fig.add_trace(
        go.Scatter(
            x=time_labels,
            y=region_df["maxT"],
            mode="lines+markers+text",
            name="最高溫 (MaxT)",
            text=[f"<b>{val}°C</b>" for val in region_df["maxT"]],
            textposition="top center",
            textfont=dict(family=MODERN_FONT, size=12, color="#E11D48"),
            line=dict(color="#F43F5E", width=3.5, shape="spline"),
            fill="tonexty",  # 填滿最低溫與最高溫之間的溫差區間
            fillcolor="rgba(14, 165, 233, 0.08)",
            marker=dict(
                size=11,
                color="#F43F5E",
                line=dict(color="#FFFFFF", width=2.5),
            ),
            hovertemplate="<b>%{x}</b><br>最高溫: <span style='color:#F43F5E;font-weight:bold;'>%{y}°C</span><extra></extra>",
        )
    )

    # 現代極簡排版設定
    fig.update_layout(
        title={
            "text": f"📈 <b>{region_name}</b> 氣溫預測區間與走勢分析",
            "x": 0.03,
            "y": 0.95,
            "xanchor": "left",
            "font": {"family": MODERN_FONT, "size": 17, "color": "#0F172A"},
        },
        font=dict(family=MODERN_FONT),
        xaxis=dict(
            title="",
            tickangle=-10,
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            tickfont=dict(size=12, color="#64748B"),
        ),
        yaxis=dict(
            title="溫度 (°C)",
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            tickfont=dict(size=12, color="#64748B"),
            range=[
                max(0, region_df["minT"].min() - 3),
                region_df["maxT"].max() + 3.5,
            ],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#475569"),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=13,
            font_family=MODERN_FONT,
            font_color="#FFFFFF",
            bordercolor="rgba(255, 255, 255, 0.15)",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=35, r=35, t=55, b=35),
        hovermode="x unified",
        height=370,
    )

    return fig


def create_multi_region_comparison_chart(all_df: pd.DataFrame, region_names: List[str]) -> go.Figure:
    """
    現代風格多縣市氣溫對比折線圖
    """
    fig = go.Figure()
    # 現代和諧色彩調色盤 (Sky, Rose, Emerald, Amber, Violet, Pink)
    palette = ["#0284C7", "#E11D48", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"]

    for idx, reg in enumerate(region_names):
        sub_df = all_df[all_df["regionName"] == reg].reset_index(drop=True)
        if sub_df.empty:
            continue

        time_labels = []
        for d in sub_df["validDate"]:
            parts = d.split("~")
            if len(parts) == 2:
                time_labels.append(f"{parts[0].strip()[5:16]}~{parts[1].strip()[11:16]}")
            else:
                time_labels.append(d)

        color = palette[idx % len(palette)]
        fig.add_trace(
            go.Scatter(
                x=time_labels,
                y=sub_df["maxT"],
                mode="lines+markers",
                name=f"{reg}",
                line=dict(color=color, width=3.2, shape="spline"),
                marker=dict(size=8, color=color, line=dict(color="#FFFFFF", width=1.5)),
                hovertemplate=f"<b>{reg}</b>: %{{y}}°C<extra></extra>",
            )
        )

    fig.update_layout(
        title={
            "text": "📊 <b>跨縣市最高氣溫預報綜合對比</b>",
            "x": 0.03,
            "y": 0.95,
            "xanchor": "left",
            "font": {"family": MODERN_FONT, "size": 17, "color": "#0F172A"},
        },
        font=dict(family=MODERN_FONT),
        xaxis=dict(title="", tickangle=-10, showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=12, color="#64748B")),
        yaxis=dict(title="最高氣溫 (°C)", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=12, color="#64748B")),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#475569"),
            bgcolor="rgba(255,255,255,0.8)",
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=13,
            font_family=MODERN_FONT,
            font_color="#FFFFFF",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=35, r=35, t=55, b=35),
        hovermode="x unified",
        height=380,
    )
    return fig
