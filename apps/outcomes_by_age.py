import os
import pandas as pd
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dateutil.relativedelta import relativedelta

from app import app

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

# data transformation
df = pd.read_csv(os.path.join(DATAPATH,"animal-shelter-data.csv"), index_col=False)
df["outcome_age_(months)"] = round(df["outcome_age_(days)"]/30)
df["raw_date"] = df["datetime"].str.split(' ').str[0]
df["Date"] = pd.to_datetime(df.raw_date)
df['Month'] = df['Date'].dt.month_name()
df['Year'] = df['Date'].dt.strftime('%Y')
df['Month_Year'] = df['Month']+'-'+df['Year'].astype(str)

# values for date pickers
start_date = min(df["Date"])
end_date = pd.Timestamp(start_date.date() + relativedelta(months=+12))

# values for dropdown menus
sexes = df['sex_upon_outcome'].unique().tolist()
breeds = df['breed'].unique().tolist()
outcomes = df['outcome_type'].unique().tolist()

# fourth page content
layout = html.Div([
    html.H3("Outcomes by Age"),
    html.Hr(),

    # row for user-selections for graphs
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="date-picker-range",
                start_date = start_date,
                min_date_allowed = min(df["Date"]),
                end_date = end_date,
                max_date_allowed = max(df["Date"]),
                persistence=True, persistence_type="local"
            )
        ], width=3),
        dbc.Col([
            html.Label("Age on outcome (months)"),
            dcc.RangeSlider(
                id="range-slider-age",
                min=min(df['outcome_age_(months)']),
                max=max(df['outcome_age_(months)']),
                value=[min(df['outcome_age_(months)']), 150],
                tooltip={"placement": "bottom", "always_visible": True},
                persistence=True, persistence_type="local"
            )
        ], width=5),
        dbc.Col([], width=1),
        dbc.Col([
            dcc.Dropdown(
                id="dropdown-breed",
                options=breeds,
                placeholder="Select breed",
                multi=True,
                persistence=True, persistence_type="local"
            )
        ], width=3)
    ]),

    # row for user-selections for stacked bar graph
    dbc.Row([
        dbc.Col([], width=6),
        dbc.Col([
            dcc.Dropdown(
                id="dropdown-outcome-age",
                options=outcomes,
                value=outcomes[1],
                clearable=False,
                persistence=True, persistence_type="local"
            )
        ], width=5),
        dbc.Col([
            dbc.Input(id="input-bins", type="number", min=5, max=100, step=1, value=12,
            persistence=True, persistence_type="local")
        ], width=1)
    ], style={'margin-top': '50px'}),
    dbc.Tooltip(
        "Filter by date of outcome",
        target="date-picker-range"
    ),
    dbc.Tooltip(
        "Bin 'age on outcome (months)' " +
        "into 'age groups (months)'",
        target="input-bins"
    ),
    dbc.Tooltip(
        "Select an outcome type",
        target="dropdown-outcome-age"
    ),

    # row for graphs and graph-specific filters
    dbc.Row([
        dbc.Col([
            dbc.Spinner(children=[dcc.Graph(id='strip-graph-age')], color='secondary')
        ], width=6),
        dbc.Col([
            dbc.Spinner(children=[dcc.Graph(id='stacked-graph')], color='secondary')
        ], width=6)
    ], style={'margin-top': '10px'})
])

@app.callback([Output("strip-graph-age", "figure"),
            Output("stacked-graph", "figure")],
            [Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("range-slider-age", "value"),
            Input("dropdown-breed", "value"),
            Input("dropdown-outcome-age", "value"),
            Input("input-bins", "value")])
def update_graphs(start_date, end_date, slider_value, dropdown2_value, outcome_value, bins_value):
    # filter by slider selection
    strip = df[(df['outcome_age_(months)'] >= slider_value[0]) & (df['outcome_age_(months)'] <= slider_value[1])]

    # filter by dropdown selection
    if (dropdown2_value != None):
        if (len(dropdown2_value) > 0):
            strip = strip[strip['breed'].isin(dropdown2_value)]

    # create new groupby data table with appropriate values for strip chart
    strip = strip[(strip['Date'] >= start_date) & (strip['Date'] <= end_date)]

    stacked = strip
    # filter by slider selection
    age_grps = pd.cut(stacked['outcome_age_(months)'], bins=bins_value, right=False).astype(str).tolist()
    age_groups = list()

    for i in range(len(age_grps)):
        age_groups.append(age_grps[i].replace('[', '').replace(')', '').replace(', ', '-'))

    stacked['age_group_(months)'] = age_groups
    stacked = stacked[stacked['outcome_type'] == outcome_value]
    stacked = pd.DataFrame(stacked.groupby(['sex_upon_outcome', 'outcome_type', 'age_group_(months)'], as_index=False)[['count']].count())
    stacked['percentage'] = 100 * stacked['count'] / stacked.groupby(['age_group_(months)'])['count'].transform('sum')

    fig1 = px.strip(strip, x="outcome_age_(months)", y="outcome_type", color="sex_upon_outcome")
    fig1.update_layout(height=550)
    fig1.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    fig2 = px.bar(stacked, x="age_group_(months)", y="percentage", color="sex_upon_outcome", color_discrete_sequence=px.colors.qualitative.Bold)
    fig2.update_layout(height=550)
    fig1.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    return fig1, fig2
