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

# sorting of stacked bar chart x-axis
months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
years = df['Year'].unique().tolist()
years = sorted(years)

sorted_month_year = list()
for i in range(len(years)):
    for j in range(len(months_order)):
        sorted_month_year.append(months_order[j] + '-' + str(years[i]))

# second page content
layout = html.Div([
    html.H3("Overview of Outcome Subtypes"),
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

    # row for graphs and graph-specific filters
    dbc.Row([
        dbc.Col([
            dbc.Spinner(children=[dcc.Graph(id='sunburst-graph')], color='secondary')
        ]),
        dbc.Col([
            dcc.Dropdown(
                id="dropdown-outcome-subtypes",
                options=outcomes,
                value=outcomes[1],
                clearable=False,
                persistence=True, persistence_type="local"
            ),
            dbc.RadioItems(
                id="radio-items-subtypes",
                options=[
                    {"label": "By day", "value": "Date"},
                    {"label": "By month", "value": "Month_Year"},
                    {"label": "By year", "value": "Year"}
                ],
                value="Month_Year",
                inline=True,
                inputCheckedClassName="border border-secondary bg-secondary",
                persistence=True, persistence_type="local"
            ),
            dbc.Spinner(children=[dcc.Graph(id='bar-graph')], color='secondary')
        ])
    ], style={'margin-top': '50px'})
])

@app.callback(Output("sunburst-graph", "figure"),
            [Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("range-slider", "value"),
            Input("dropdown-sex", "value"),
            Input("dropdown-breed", "value")])
def update_sunburst(start_date, end_date, slider_value, dropdown1_value, dropdown2_value):
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
    final = pd.DataFrame(final.groupby(["outcome_type", "outcome_subtype"], as_index=False)["count"].count())

    fig = px.sunburst(final, path=['outcome_type', 'outcome_subtype'], values='count',
        color_discrete_sequence=px.colors.qualitative.Bold)

    return fig

@app.callback(Output("bar-graph", "figure"),
            [Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("range-slider", "value"),
            Input("dropdown-sex", "value"),
            Input("dropdown-breed", "value"),
            Input("dropdown-outcome-subtypes", "value"),
            Input("radio-items-subtypes", "value")])
def update_bargraph(start_date, end_date, slider_value, dropdown1_value, dropdown2_value, outcome_value, radio_value):
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
    final = pd.DataFrame(final.groupby([radio_value, "outcome_type", "outcome_subtype"], as_index=False)["count"].count())
    final = final[final['outcome_type'] == outcome_value]

    fig = px.bar(final, x=radio_value, y="count", color="outcome_subtype", color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_xaxes(categoryorder='array', categoryarray=sorted_month_year)

    return fig
