"""
chart_avg_weekday.py
Average occupancy per hour for each weekday with selectable timespan.
- x-axis: hour
- y-axis: occupancy (%)
- legend: weekday
- Plotly dropdown: last 1 month, 3 months, 6 months, all data
"""

from charts.chart_base import ChartBase
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


class AverageWeekdayChart(ChartBase):
    name = "avg_weekday"
    title = "Average per Weekday"
    priority = 5

    def render(self):
        df = self.df.copy()
        if df.empty:
            return {"title": self.title, "html": "<p>No data available.</p>"}

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["weekday"] = df["timestamp"].dt.weekday
        df["hour"] = df["timestamp"].dt.hour
        df["weekday_name"] = df["weekday"].map({0:"Mo",1:"Di",2:"Mi",3:"Do",4:"Fr",5:"Sa",6:"So"})

        # Define timespans in days
        timespans = [
            (30, "Last 1 month"),
            (90, "Last 3 months"),
            (180, "Last 6 months"),
            (0, "All")
        ]

        traces = []
        buttons = []

        for span_days, label in timespans:
            if span_days > 0:
                since = datetime.now() - timedelta(days=span_days)
                df_span = df[df["timestamp"] >= since]
            else:
                df_span = df

            avg = df_span.groupby(["weekday", "hour"])["occupancy"].mean().reset_index()
            avg["weekday_name"] = avg["weekday"].map({0:"Mo",1:"Di",2:"Mi",3:"Do",4:"Fr",5:"Sa",6:"So"})

            # Create traces per weekday
            span_traces = []
            for wd in sorted(avg["weekday"].unique()):
                sub = avg[avg["weekday"] == wd]
                trace = go.Scatter(
                    x=sub["hour"],
                    y=sub["occupancy"],
                    mode="lines+markers",
                    name=sub["weekday_name"].iloc[0],
                    visible=(label=="Last 1 month")  # default visible = 1 month
                )
                span_traces.append(trace)
                traces.append(trace)

            # Visibility mask for dropdown
            mask = [False] * len(traces)
            start_idx = len(traces) - len(span_traces)
            for i in range(start_idx, len(traces)):
                mask[i] = True

            buttons.append(dict(
                label=label,
                method="update",
                args=[{"visible": mask}, {"title": f"{self.title} — {label}"}]
            ))

        layout = go.Layout(
            title=f"{self.title} — Last 1 month",
            xaxis=dict(title="Hour", dtick=1),
            yaxis=dict(title="Avg Occupancy (%)", range=[0, 100]),
            updatemenus=[dict(buttons=buttons, x=0.0, y=1.15, xanchor="left", direction="down")],
            legend=dict(title="Weekday")
        )

        fig = go.Figure(data=traces, layout=layout)
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))

        return {"title": self.title, "html": fig.to_html(full_html=False)}
