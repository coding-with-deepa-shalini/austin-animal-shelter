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
colours = df['color'].unique().tolist()
outcomes = df['outcome_type'].unique().tolist()

# fifth page content
layout = html.Div([
    html.H3("Outcomes by Breed"),
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
                value=[min(df['outcome_age_(months)']), 24],
                tooltip={"placement": "bottom", "always_visible": True},
                persistence=True, persistence_type="local"
            )
        ], width=5),
        dbc.Col([
            dbc.Switch(
                id="cfa-switch",
                label="CFA breeds",
                value=True,
                persistence=True, persistence_type="local"
            )
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id="dropdown-colour",
                options=colours,
                placeholder="Select colour",
                multi=True,
                persistence=True, persistence_type="local"
            )
        ], width=2)
    ]),
    dbc.Tooltip(
        "Filter by date of outcome",
        target="date-picker-range"
    ),

    # row for graph
    dbc.Row([
        dbc.Col([
            dbc.Spinner(children=[dcc.Graph(id='scatter-graph-breed')], color='secondary')
        ])
    ])
])

@app.callback(Output("scatter-graph-breed", "figure"),
            [Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("range-slider-age", "value"),
            Input("dropdown-colour", "value"),
            Input("cfa-switch", "value")])
def update_scatter_chart(start_date, end_date, slider_value, dropdown2_value, switch_value):
    # filter by slider selection
    strip = df[(df['outcome_age_(months)'] >= slider_value[0]) & (df['outcome_age_(months)'] <= slider_value[1])]

    # filter by dropdown selection
    if (dropdown2_value != None):
        if (len(dropdown2_value) > 0):
            strip = strip[strip['color'].isin(dropdown2_value)]

    # create new groupby data table with appropriate values for strip chart
    strip = strip[(strip['Date'] >= start_date) & (strip['Date'] <= end_date)]
    strip = strip[strip['cfa_breed'] == switch_value]

    final = pd.DataFrame(strip.groupby(['breed', 'outcome_type', 'sex_upon_outcome'], as_index=False)['count'].count())

    fig = px.scatter(final, x="breed", y="outcome_type", size='count', color="sex_upon_outcome",
        color_discrete_sequence=px.colors.qualitative.Light24)
    fig.update_layout(autosize=False, width=1600, height=650)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    return fig
