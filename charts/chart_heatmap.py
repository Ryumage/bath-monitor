"""
chart_heatmap.py
Heatmap plugin: date vs hour heatmap showing average occupancy.

Interactive control: Plotly supports zoom and colorbar interactions.
"""

from charts.chart_base import ChartBase
import pandas as pd
import plotly.express as px


class HeatmapChart(ChartBase):
    name = "heatmap"
    title = "Heatmap"
    priority = 2

    def render(self):
        df = self.df.copy()
        if df.empty:
            return {"title": self.title, "html": "<p>No data available.</p>"}

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["date"] = df["timestamp"].dt.date

        pivot = df.pivot_table(index="date", columns="hour", values="occupancy", aggfunc="mean")
        # Fill missing hours with NaN — plotly handles it
        fig = px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="YlOrRd",
            labels=dict(x="Hour", y="Date", color="Occupancy (%)"),
            title=self.title
        )
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        return {"title": self.title, "html": fig.to_html(full_html=False)}
