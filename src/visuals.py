"""
src/visuals.py - Plotly Financial Visualization Module
Generates professional investment-grade plots for the Streamlit dashboard layout.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any

def create_sentiment_gauge(score: float) -> go.Figure:
    """
    Creates a beautiful gauge chart showing the overall sentiment score on a -10 to +10 scale.
    """
    # Normalize score from -10/+10 to 0/100% or just map it elegantly
    # Color map: red for negative, yellow for neutral, green for positive
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Management Sentiment Score", 'font': {'size': 18, 'color': '#2C3E50'}},
        gauge = {
            'axis': {'range': [-10, 10], 'tickwidth': 1, 'tickcolor': "#7F8C8D"},
            'bar': {'color': "#2C3E50"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#BDC3C7",
            'steps': [
                {'range': [-10, -3], 'color': '#FFCDD2'},  # Soft red
                {'range': [-3, 3], 'color': '#FFE082'},    # Soft yellow
                {'range': 3, 10, 'color': '#C8E6C9'}      # Soft green
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=250, 
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_strategic_focus_chart(focus_data: Dict[str, float]) -> go.Figure:
    """
    Generates a professional donut chart depicting the allocation of management focus.
    """
    labels = [k.replace('_', ' ').title() for k in focus_data.keys()]
    values = list(focus_data.values())
    
    # Elegant investor palette
    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#9467BD']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.4,
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
        textinfo='label+percent',
        hoverinfo='label+value'
    )])
    
    fig.update_layout(
        title={'text': "Management Strategic Focus Allocations", 'font': {'size': 16, 'color': '#2C3E50'}},
        showlegend=False,
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_keyword_bar_chart(keyword_frequencies: Dict[str, int]) -> go.Figure:
    """
    Creates a clean, horizontal bar chart highlighting discussions on key corporate themes.
    """
    # Convert to DataFrame and sort
    df = pd.DataFrame({
        "Keyword": [k.title() for k in keyword_frequencies.keys()],
        "Occurrences": list(keyword_frequencies.values())
    }).sort_values(by="Occurrences", ascending=True)
    
    # Take top 10 for neatness
    df = df.tail(10)
    
    fig = px.bar(
        df, 
        x="Occurrences", 
        y="Keyword", 
        orientation='h',
        color="Occurrences",
        color_continuous_scale=px.colors.sequential.Bluyl
    )
    
    fig.update_layout(
        title={'text': "Corporate Vocabulary Word Frequencies", 'font': {'size': 16, 'color': '#2C3E50'}},
        xaxis_title="Count",
        yaxis_title=None,
        coloraxis_showscale=False,
        height=320,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#EFEFEF')
    return fig
