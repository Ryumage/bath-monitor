"""
chart_base.py

Base class for chart plugins. Plugins live in the "charts" package and must
inherit from ChartBase. They should implement render() returning a dict:
    {"title": "<Title>", "html": "<plotly html>"}
"""

from abc import ABC, abstractmethod


class ChartBase(ABC):
    name: str = "unnamed"
    title: str = "Untitled"
    priority: int = 999

    def __init__(self, bath: str, df):
        """
        :param bath: bath key (table name)
        :param df: pandas DataFrame with the bath data (timestamp parsed as datetime)
        """
        self.bath = bath
        self.df = df

    @abstractmethod
    def render(self):
        """
        Produce the chart. Return dict with 'title' and 'html'.
        """
        raise NotImplementedError
