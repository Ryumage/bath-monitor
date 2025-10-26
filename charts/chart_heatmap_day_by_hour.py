"""
chart_heatmap_day_by_hour.py
----------------
Heatmap of occupancy by day and hour.
"""

import plotly.express as px
import pandas as pd
from charts.chart_base import ChartBase


class HeatmapChart(ChartBase):
    name = "heatmap_by_hour_and_day"
    title = "Heatmap per day"
    priority = 2

    def render(self):
        df = self.df.copy()
        df["day"] = pd.to_datetime(df["timestamp"]).dt.strftime("%a")
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour

        pivot = (
            df.groupby(["day", "hour"])["occupancy"]
            .mean()
            .reset_index()
            .pivot(index="day", columns="hour", values="occupancy")
        )

        fig = px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="YlOrRd",
            title="Occupancy Heatmap by Day & Hour",
            labels={"x": "Hour", "y": "Day", "color": "Occupancy (%)"},
        )
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        return {"title": self.title, "html": fig.to_html(full_html=False)}
