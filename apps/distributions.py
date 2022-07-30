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

# third page content
layout = html.Div([
    html.H3("Distributions"),
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
                id="range-slider",
                min=min(df['outcome_age_(months)']),
                max=max(df['outcome_age_(months)']),
                value=[min(df['outcome_age_(months)']), 12],
                tooltip={"placement": "bottom", "always_visible": True},
                persistence=True, persistence_type="local"
            )
        ], width=4),
        dbc.Col([], width=1),
        dbc.Col([
            dcc.Dropdown(
                id="dropdown-sex",
                options=sexes,
                placeholder="Select sex",
                multi=True,
                persistence=True, persistence_type="local"
            )
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id="dropdown-breed",
                options=breeds,
                placeholder="Select breed",
                multi=True,
                persistence=True, persistence_type="local"
            )
        ], width=2)
    ]),
    dbc.Tooltip(
        "Filter by date of outcome",
        target="date-picker-range"
    ),

    # row for outcome selection
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="dropdown-outcome-dist",
                options=outcomes,
                value=outcomes[1],
                clearable=False,
                persistence=True, persistence_type="local"
            )
        ])
    ], style={'margin-top': '50px'}),

    # row for secondary dropdown menus for further filtering of histograms
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="dropdown-col1", placeholder="Select weekday",
            persistence=True, persistence_type="local")
        ], width=4),
        dbc.Col([
            dcc.Dropdown(id="dropdown-col2", placeholder="Select month",
            persistence=True, persistence_type="local")
        ], width=4),
        dbc.Col([
            dcc.Dropdown(id="dropdown-col3", placeholder="Select year",
            persistence=True, persistence_type="local")
        ], width=4)
    ], style={'margin-top': '20px'}),

    # row for graphs
    dbc.Row([
        dbc.Col([
            dbc.Spinner(children=[dcc.Graph(id='hist-hour')], color='secondary')
        ], width=4),
        dbc.Col([
            dbc.Spinner(children=[dcc.Graph(id='hist-weekday')], color='secondary')
        ], width=4),
        dbc.Col([
            dbc.Spinner(children=[dcc.Graph(id='hist-month')], color='secondary')
        ], width=4)
    ])
])

@app.callback([Output("dropdown-col1", "options"),
            Output("dropdown-col2", "options"),
            Output("dropdown-col3", "options")],
            [Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("range-slider", "value"),
            Input("dropdown-sex", "value"),
            Input("dropdown-breed", "value"),
            Input("dropdown-outcome-dist", "value")])
def update_secondary_dropdowns(start_date, end_date, slider_value, dropdown1_value, dropdown2_value, outcome_value):
    # filter by slider selection
    final = df[(df['outcome_age_(months)'] >= slider_value[0]) & (df['outcome_age_(months)'] <= slider_value[1])]

    # filter by dropdown selections
    if (dropdown1_value != None):
        if (len(dropdown1_value) > 0):
            final = final[final['sex_upon_outcome'].isin(dropdown1_value)]

    if (dropdown2_value != None):
        if (len(dropdown2_value) > 0):
            final = final[final['breed'].isin(dropdown2_value)]

    # create new groupby data table with appropriate values for sunburst chart
    final = final[(final['Date'] >= start_date) & (final['Date'] <= end_date)]
    final = final[final['outcome_type'] == outcome_value]

    options1 = final['outcome_weekday'].unique().tolist()
    options2 = final['outcome_month'].unique().tolist()
    options3 = final['outcome_year'].unique().tolist()

    return options1, sorted(options2), sorted(options3)


@app.callback([Output("hist-hour", "figure"),
            Output("hist-weekday", "figure"),
            Output("hist-month", "figure")],
            [Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("range-slider", "value"),
            Input("dropdown-sex", "value"),
            Input("dropdown-breed", "value"),
            Input("dropdown-outcome-dist", "value"),
            Input("dropdown-col1", "value"),
            Input("dropdown-col2", "value"),
            Input("dropdown-col3", "value")])
def update_histograms(start_date, end_date, slider_value, dropdown1_value, dropdown2_value, outcome_value, dropdown_col1, dropdown_col2, dropdown_col3):
    # filter by slider selection
    final = df[(df['outcome_age_(months)'] >= slider_value[0]) & (df['outcome_age_(months)'] <= slider_value[1])]

    # filter by dropdown selections
    if (dropdown1_value != None):
        if (len(dropdown1_value) > 0):
            final = final[final['sex_upon_outcome'].isin(dropdown1_value)]

    if (dropdown2_value != None):
        if (len(dropdown2_value) > 0):
            final = final[final['breed'].isin(dropdown2_value)]

    # create new groupby data table with appropriate values for sunburst chart
    final = final[(final['Date'] >= start_date) & (final['Date'] <= end_date)]
    final = final[final['outcome_type'] == outcome_value]

    # filter by user-selection in the secondary dropdowns
    hours_df = final
    weekdays_df = final
    months_df = final

    if (dropdown_col1 != None):
        hours_df = final[final['outcome_weekday'] == dropdown_col1]

    if (dropdown_col2 != None):
        weekdays_df = final[final['outcome_month'] == dropdown_col2]

    if (dropdown_col3 != None):
        months_df = final[final['outcome_year'] == dropdown_col3]

    hour = px.histogram(hours_df, x="outcome_hour", color="outcome_subtype", marginal="violin", title="Outcomes by hour of day")
    hour.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    weekday = px.histogram(weekdays_df, x="outcome_weekday", color="outcome_subtype", marginal="violin", title="Outcomes by day of week")
    weekday.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    month = px.histogram(months_df, x="outcome_month", color="outcome_subtype", marginal="violin", title="Outcomes by month of year")
    month.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    return hour, weekday, month
