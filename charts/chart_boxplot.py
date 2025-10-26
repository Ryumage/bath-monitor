"""
chart_boxplot.py
Boxplot per hour. Provides Plotly buttons to switch days window (30 / 60 / all).
"""

from charts.chart_base import ChartBase
import plotly.express as px
import pandas as pd


class BoxplotChart(ChartBase):
    name = "boxplot"
    title = "Boxplot per Hour"
    priority = 4

    def render(self):
        df = self.df.copy()
        if df.empty:
            return {"title": self.title, "html": "<p>No data available.</p>"}
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["date"] = df["timestamp"].dt.date

        # Build 3 figures and embed as a single Plotly figure with buttons:
        # We'll make traces grouped by date windows and toggle visibility.

        # Prepare windows: 30,60,all
        windows = [30, 60, None]  # None == all
        traces = []
        visibility_matrix = []
        total_traces = 0

        # We'll produce box traces per hour aggregated for each window
        # For simpler toggling, produce separate figures and then merge traces.
        figs = []
        for w in windows:
            if w is None:
                df_w = df.copy()
                label = "All"
            else:
                cutoff = df["timestamp"].max() - pd.Timedelta(days=w)
                df_w = df[df["timestamp"] >= cutoff]
                label = f"Last {w} days"

            if df_w.empty:
                figs.append(None)
                continue

            fig_w = px.box(
                df_w,
                x="hour",
                y="occupancy",
                labels={"hour": "Hour", "occupancy": "Occupancy (%)"},
                title=f"{self.title} — {label}"
            )
            figs.append(fig_w)

        # If only one fig exists, return it
        valid_figs = [f for f in figs if f is not None]
        if not valid_figs:
            return {"title": self.title, "html": "<p>No data for chosen windows.</p>"}
        if len(valid_figs) == 1:
            fig = valid_figs[0]
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            return {"title": self.title, "html": fig.to_html(full_html=False)}

        # Merge traces and create buttons to toggle visibility
        merged = valid_figs[0].to_dict()
        # Build merged figure by using the first figure and adding the rest traces
        import plotly.graph_objects as go
        fig = go.Figure()
        for idx, f in enumerate(valid_figs):
            for tr in f.data:
                fig.add_trace(tr)
        # Build visibility groups: each window has len(traces_in_fig) traces
        counts = [len(f.data) for f in valid_figs]
        total = sum(counts)
        vis_buttons = []
        start = 0
        for i, cnt in enumerate(counts):
            vis = [False] * total
            for j in range(start, start + cnt):
                vis[j] = True
            start += cnt
            vis_buttons.append(vis)

        button_defs = []
        labels = ["Last 30", "Last 60", "All"]
        for vis, lab in zip(vis_buttons, labels):
            button_defs.append(dict(
                label=lab,
                method="update",
                args=[{"visible": vis}, {"title": f"{self.title} — {lab} days"}]
            ))

        fig.update_layout(
            updatemenus=[dict(buttons=button_defs, x=0.0, y=1.15, xanchor="left", direction="down")],
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(title="Hour")
        )

        return {"title": self.title, "html": fig.to_html(full_html=False)}
