"""
chart_weekday_compare.py

Compare the same weekday across the last 6 occurrences (weeks).
- x-axis: hour of day (decimal hour)
- y-axis: occupancy (%)
- one trace per date (same weekday)
- Plotly updatemenu (dropdown) to pick weekday (Mon..Sun)
- default selection = today's weekday (if data exists), otherwise first available weekday
- robust about missing weekdays, legend visible, and title updates dynamically
"""

from charts.chart_base import ChartBase
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from typing import List, Tuple


class WeekdayCompareChart(ChartBase):
    name = "weekday_compare"
    title = "Weekday Comparison"
    priority = 2

    def render(self):
        df = self.df.copy()
        if df.empty:
            return {"title": self.title, "html": "<p>No data available.</p>"}

        # Normalize timestamp and compute helpers
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour + df["timestamp"].dt.minute / 60.0
        df["date"] = df["timestamp"].dt.date
        df["weekday_num"] = df["timestamp"].dt.weekday  # 0=Mon ... 6=Sun

        weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        today_wd = datetime.now().weekday()

        # For each weekday that has data, collect the last N (6) dates
        weekday_date_groups: List[Tuple[int, List[pd.Timestamp]]] = []
        for wd in range(7):
            sub = df.loc[df["weekday_num"] == wd]
            if sub.empty:
                continue
            unique_dates = sorted(sub["date"].unique())[-6:]  # last up to 6
            weekday_date_groups.append((wd, unique_dates))

        if not weekday_date_groups:
            return {"title": self.title, "html": "<p>No weekday data available.</p>"}

        # Build traces and remember start/end indices
        traces: List[go.Scatter] = []
        groups_idx: List[Tuple[int, int, int]] = []  # (weekday_num, start_idx, end_idx)
        for wd, dates in weekday_date_groups:
            start = len(traces)
            for d in dates:
                day_rows = df[(df["weekday_num"] == wd) & (df["date"] == d)].sort_values("hour")
                if day_rows.empty:
                    continue
                name = f"{weekday_labels[wd]} {d}"  # legend label
                traces.append(go.Scatter(
                    x=day_rows["hour"],
                    y=day_rows["occupancy"],
                    mode="lines+markers",
                    name=name,
                    visible=False
                ))
            end = len(traces)
            groups_idx.append((wd, start, end))

        total_traces = len(traces)

        # Helper to compute visibility mask for a given weekday_group index
        def mask_for_group(group_index: int) -> List[bool]:
            mask = [False] * total_traces
            _, start, end = groups_idx[group_index]
            for i in range(start, end):
                mask[i] = True
            return mask

        # Build the updatemenu buttons and map weekday -> button index
        buttons = []
        wd_to_button_index = {}
        for idx, (wd, start, end) in enumerate(groups_idx):
            if end - start == 0:
                continue
            label = weekday_labels[wd]
            # FIX: method="update" to allow title change + visibility
            buttons.append(dict(
    label=label,
    method="update",  # bleibt update, wir geben jetzt beide args sauber an
    args=[
        {"visible": mask_for_group(idx)},  # update traces visibility
        {"title": {"text": f"{self.title} — {label}"}}  # update title safely
    ]
))
            wd_to_button_index[wd] = len(buttons) - 1

        # Determine the default active button index
        if today_wd in wd_to_button_index:
            active_button_index = wd_to_button_index[today_wd]
            default_group_index = next(i for i, (wd, _, _) in enumerate(groups_idx) if wd == today_wd)
        else:
            active_button_index = 0
            default_group_index = 0

        # Build figure
        fig = go.Figure(data=traces)
        # Set visibility for default
        visible_mask = mask_for_group(default_group_index)
        any_visible = any(visible_mask)
        if not any_visible and total_traces > 0:
            visible_mask[0] = True
        for i, v in enumerate(visible_mask):
            fig.data[i].visible = v

        # Layout
        fig.update_layout(
            title=f"{self.title} — {weekday_labels[groups_idx[default_group_index][0]]}",
            xaxis=dict(title="Hour of Day", dtick=1),
            yaxis=dict(title="Occupancy (%)", range=[0, 100]),
            legend=dict(title="Date"),
            updatemenus=[dict(
                buttons=buttons,
                direction="down",
                x=0.0, y=1.15,
                xanchor="left",
                showactive=True,
                active=active_button_index
            )]
        )

        return {"title": self.title, "html": fig.to_html(full_html=False)}
