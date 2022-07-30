import os
import pandas as pd
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
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
end_date = pd.Timestamp(start_date.date() + relativedelta(months=+36))

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

# first page content
layout = html.Div([
    html.H3("Overview of Outcomes", style={'display': 'inline'}),
    dbc.Button("KPIs", id="button-kpis", color='secondary', n_clicks=0, style={'display': 'inline', 'float': 'right'}),
    dbc.Modal([
        dbc.ModalHeader("Set Key Performance Indices (KPIs)"),
        dbc.ModalBody([
            dcc.Dropdown(
                id="dropdown-kpi1",
                options=outcomes,
                value=outcomes[1],
                clearable=False,
                persistence=True, persistence_type="local"
            ),
            html.Br(),
            dcc.Dropdown(
                id="dropdown-kpi2",
                options=outcomes,
                value=outcomes[0],
                clearable=False,
                persistence=True, persistence_type="local"
            ),
            html.Br(),
            dcc.Dropdown(
                id="dropdown-kpi3",
                options=outcomes,
                value=outcomes[2],
                clearable=False,
                persistence=True, persistence_type="local"
            )
        ])
    ], id="modal-kpis", is_open=False, centered=True),
    html.Hr(),

    # row for user-selections to change KPIs and graph
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="date-picker-range-overview",
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
    ], style={'margin-bottom': '40px'}),
    dbc.Tooltip(
        "Filter by date of outcome",
        target="date-picker-range-overview"
    ),
    dbc.Tooltip(
        "Set the KPIs to be displayed",
        target="button-kpis"
    ),

    # row for KPIs
    dbc.Row([
        dbc.Col([], width=1),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H1({}, id='kpi1', className='card-title'),
                ]),
                dbc.CardFooter([], id="kpi1-title")
            ], color="secondary", outline=True)
        ], width=2),
        dbc.Col([], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H1({}, id='kpi2', className='card-title'),
                ]),
                dbc.CardFooter([], id="kpi2-title")
            ], color="secondary", outline=True)
        ], width=2),
        dbc.Col([], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H1({}, id='kpi3', className='card-title'),
                ]),
                dbc.CardFooter([], id="kpi3-title")
            ], color="secondary", outline=True)
        ], width=2),
        dbc.Col([], width=1)
    ]),

    # row for graph and graph-specific filters
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(
                id="radio-items-outcomes",
                options=[
                    {"label": "By day", "value": "Date"},
                    {"label": "By month", "value": "Month_Year"},
                    {"label": "By year", "value": "Year"}
                ],
                value="Month_Year",
                labelStyle={'display': 'block'},
                className="align-items-center",
                inputCheckedClassName="border border-secondary bg-secondary",
                persistence=True, persistence_type="local"
            )
        ], width=1),
        dbc.Col([
            dbc.Spinner(children=[dcc.Graph(id='gross-outcomes')], color='secondary')
        ], width=11)
    ], style={'margin-top': '40px'})
])

@app.callback(Output("modal-kpis", "is_open"),
            [Input("button-kpis", "n_clicks")],
            [State("modal-kpis", "is_open")])
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback([Output("kpi1", "children"),
            Output("kpi2", "children"),
            Output("kpi3", "children"),
            Output("kpi1-title", "children"),
            Output("kpi2-title", "children"),
            Output("kpi3-title", "children")],
            [Input("date-picker-range-overview", "start_date"),
            Input("date-picker-range-overview", "end_date"),
            Input("range-slider", "value"),
            Input("dropdown-kpi1", "value"),
            Input("dropdown-kpi2", "value"),
            Input("dropdown-kpi3", "value"),
            Input("dropdown-sex", "value"),
            Input("dropdown-breed", "value")])
def update_adoptions_pie(start_date, end_date, slider_value, dropdown_kpi1, dropdown_kpi2, dropdown_kpi3, dropdown1_value, dropdown2_value):
    # filter by slider selection
    final = df[(df['outcome_age_(months)'] >= slider_value[0]) & (df['outcome_age_(months)'] <= slider_value[1])]

    # filter by dropdown selections
    if (dropdown1_value != None):
        if (len(dropdown1_value) > 0):
            final = final[final['sex_upon_outcome'].isin(dropdown1_value)]

    if (dropdown2_value != None):
        if (len(dropdown2_value) > 0):
            final = final[final['breed'].isin(dropdown2_value)]

    final = final[(final['Date'] >= start_date) & (final['Date'] <= end_date)]
    final = pd.DataFrame(final.groupby(['outcome_type'], as_index=False)['count'].count())
    total = sum(final['count'])

    try:
        kpi1_df = final[final['outcome_type'] == dropdown_kpi1]
        kpi2_df = final[final['outcome_type'] == dropdown_kpi2]
        kpi3_df = final[final['outcome_type'] == dropdown_kpi3]

        kpi1 = int(kpi1_df['count'])
        kpi2 = int(kpi2_df['count'])
        kpi3 = int(kpi3_df['count'])

        kpi1_percentage = round(kpi1 / total * 100, 2)
        kpi2_percentage = round(kpi2 / total * 100, 2)
        kpi3_percentage = round(kpi3 / total * 100, 2)

    except:
        kpi1_percentage = 0
        kpi2_percentage = 0
        kpi3_percentage = 0

    return str(kpi1_percentage) + "%", str(kpi2_percentage) + "%", str(kpi3_percentage) + "%", dropdown_kpi1, dropdown_kpi2, dropdown_kpi3

@app.callback(Output("gross-outcomes", "figure"),
            [Input("date-picker-range-overview", "start_date"),
            Input("date-picker-range-overview", "end_date"),
            Input("range-slider", "value"),
            Input("dropdown-sex", "value"),
            Input("dropdown-breed", "value"),
            Input("radio-items-outcomes", "value")])
def update_graph(start_date, end_date, slider_value, dropdown1_value, dropdown2_value, radio_value):
    # filter by slider selection
    final = df[(df['outcome_age_(months)'] >= slider_value[0]) & (df['outcome_age_(months)'] <= slider_value[1])]

    # filter by dropdown selections
    if (dropdown1_value != None):
        if (len(dropdown1_value) > 0):
            final = final[final['sex_upon_outcome'].isin(dropdown1_value)]

    if (dropdown2_value != None):
        if (len(dropdown2_value) > 0):
            final = final[final['breed'].isin(dropdown2_value)]

    # create new groupby data table with appropriate values for area chart
    final = final[(final['Date'] >= start_date) & (final['Date'] <= end_date)]
    final = pd.DataFrame(final.groupby([radio_value, "outcome_type"], as_index=False)["count"].count())

    fig = px.area(final, x=radio_value, y="count", color="outcome_type")
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_xaxes(categoryorder='array', categoryarray=sorted_month_year)

    return fig
