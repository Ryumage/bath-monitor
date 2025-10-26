"""
chart_line.py
Line chart plugin.

- One line per day (x axis = hour of day).
- Adds Plotly updatemenu buttons to show current week, last week, etc.
"""

from charts.chart_base import ChartBase
import pandas as pd
import plotly.graph_objects as go


class LineChart(ChartBase):
    name = "line"
    title = "Line Chart"
    priority = 1

    def render(self):
        df = self.df.copy()
        if df.empty:
            return {"title": self.title, "html": "<p>No data available.</p>"}

        # ensure timestamp column is datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # basic time columns
        df["hour"] = df["timestamp"].dt.hour + df["timestamp"].dt.minute / 60.0
        df["date"] = df["timestamp"].dt.date
        df["weekday"] = df["timestamp"].dt.strftime("%a")  # e.g. Mon, Tue
        df["week"] = df["timestamp"].dt.isocalendar().week
        df["year"] = df["timestamp"].dt.isocalendar().year

        # determine current week
        current_year = df["year"].max()
        current_week = df[df["year"] == current_year]["week"].max()

        # helper to get traces for a specific week
        def traces_for_week(week_num, year_num):
            traces = []
            week_df = df[(df["week"] == week_num) & (df["year"] == year_num)]
            if week_df.empty:
                return traces
            for date_val in sorted(week_df["date"].unique()):
                sub = week_df[week_df["date"] == date_val].sort_values("hour")
                weekday = sub["weekday"].iloc[0]
                traces.append(go.Scatter(
                    x=sub["hour"],
                    y=sub["occupancy"],
                    mode="lines+markers",
                    name=f"{weekday} {date_val}",
                    visible=True
                ))
            return traces

        # collect up to 4 weeks (current, last, -2, -3)
        all_weeks = []
        for i in range(4):
            target_week = current_week - i
            year = current_year
            if target_week <= 0:  # handle year crossover
                year -= 1
                target_week = 52 + target_week
            all_weeks.append((target_week, year))

        # create traces for all 4 weeks, initially show only current
        all_traces = []
        week_indices = []
        for (week_num, year_num) in all_weeks:
            traces = traces_for_week(week_num, year_num)
            week_indices.append(len(traces))
            all_traces.extend(traces)

        total_traces = len(all_traces)

        # visibility masks for updatemenu
        def week_mask(week_index):
            mask = [False] * total_traces
            start = sum(week_indices[:week_index])
            end = start + week_indices[week_index]
            for i in range(start, end):
                mask[i] = True
            return mask

        buttons = []
        week_labels = ["Current week", "Last week", "2 weeks ago", "3 weeks ago"]
        for i, label in enumerate(week_labels):
            if i >= len(week_indices):
                continue
            buttons.append(dict(
                label=label,
                method="update",
                args=[{"visible": week_mask(i)}, {"title": f"{self.title} — {label}"}]
            ))

        # layout and figure
        layout = go.Layout(
            title=f"{self.title} — Current week",
            xaxis=dict(title="Hour of Day", dtick=1),
            yaxis=dict(title="Occupancy (%)", range=[0, 100]),
            autosize=True,
            updatemenus=[dict(
                buttons=buttons,
                x=0.0, y=1.15,
                xanchor="left",
                direction="down",
                showactive=True,
            )]
        )

        fig = go.Figure(data=all_traces, layout=layout)

        return {"title": self.title, "html": fig.to_html(full_html=False)}
