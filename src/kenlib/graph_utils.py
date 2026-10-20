import pandas as pd

import kenlib.config_utils as cu
import kenlib.df_utils as dfu

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

class GraphPlot:

    _fig:go.Figure

    def __init__(self, title: str = ""):
        self.lastcolor = -1
        self.title=title
        self._fig = make_subplots(specs=[[{"secondary_y": True}]])

        self._fig.update_layout(
            autosize=True,
            width=None,
            margin=dict(l=10, r=10, t=40, b=10),
            title_text=title,
            hovermode="x unified", 
            template="plotly_white",
            legend=dict(
                orientation="h", 
                yanchor="top",  
                y=-0.15,   
                xanchor="center", 
                x=0.5     
            )
        )
    def addtimeseries(self, df, xvalue, yvalue, seriestitle="", colorseq=-1, rightaxis: bool = False,units:str="Scale"):
        if colorseq == -1:
            colorseq = self.lastcolor + 1

        df=df.sort_values(by=xvalue)
        # Handle dual axis calculation seamlessly
        self._fig.add_trace(
            go.Scatter(
                x=df[xvalue], 
                y=df[yvalue], 
                name=seriestitle,
                line=dict(color=self.graph_colorlist(colorseq), width=3)
            ),
            secondary_y=rightaxis, # Tells Plotly to map this to the RIGHT axis
        )

        self._fig.update_yaxes(title_text=units, secondary_y=rightaxis)


        self.lastcolor = colorseq

    @property
    def fig(self)->go.Figure:
        return self._fig

    def stream(self):
        st.plotly_chart(self._fig, use_container_width=True)

    def graph_colorlist(self, colorseq: int):
        colorarray = [
            "blue", "darkorange", "green", "crimson", 
            "purple", "gold", "darkturquoise", "dimgrey"
        ]
        return colorarray[colorseq % len(colorarray)]
