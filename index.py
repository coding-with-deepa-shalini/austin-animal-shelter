# -*- coding: utf-8 -*-

import os
from dash import dcc
from dash import html
import dash_extensions as de
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app
from app import server
from apps import outcomes_overview, outcome_subtypes_overview, distributions, outcomes_by_age, outcomes_by_breed

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
options = dict(loop=True, autoplay=True) #rendererSettings=dict(preserveAspectRatio='xMidYmid slice'

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "color": "#7F7F7F",
    "background-color": "#EBEBEB",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.Br(),
        html.Br(),
        html.A(
            html.Img(
                src=app.get_asset_url('austin-animal-center-logo-wide.jpeg'), height="110px"
            ),
            title="Austin Animal Shelter",
            href="https://www.austintexas.gov/austin-animal-center/",
            target="_blank"
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Outcomes", href="/outcomes-overview", active="exact"),
                dbc.NavLink("Outcome Subtypes", href="/outcomes-subtypes-overview", active="exact"),
                dbc.NavLink("Distributions", href="/distributions", active="exact"),
                dbc.NavLink("Outcomes by Age", href="/outcomes-by-age", active="exact"),
                dbc.NavLink("Outcomes by Breed", href="/outcomes-by-breed", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

sm_bar = dbc.Row(
    [
        dbc.Col(html.A(html.Img(src=app.get_asset_url('facebook-icon.png'), height="27px", className="mr-3", style={'margin-top':10, 'margin-bottom':10}), href="https://www.facebook.com/austintexasgov/", target="_blank")),
        dbc.Col(html.A(html.Img(src=app.get_asset_url('insta-icon.png'), height="27px", className="mr-3", style={'margin-top':11, 'margin-bottom':9}), href="https://www.instagram.com/austintexasgov/", target="_blank")),
        dbc.Col(html.A(html.Img(src=app.get_asset_url('twitter-icon.png'), height="25px", className="mr-3", style={'margin-top':11, 'margin-bottom':9}), href="https://twitter.com/austintexasgov/", target="_blank")),
        dbc.Col(html.A(html.Img(src=app.get_asset_url('linkedin-icon.png'), height="23px", className="mr-3", style={'margin-top':10, 'margin-bottom':10}), href="https://www.linkedin.com/company/city-of-austin/", target="_blank")),
        dbc.Col(html.A(html.Img(src=app.get_asset_url('youtube-icon.png'), height="25px", className="mr-3", style={'margin-top':11, 'margin-bottom':9}), href="https://www.youtube.com/user/austintexasgov/", target="_blank")),
    ],
    className="ms-auto g-3 pe-4",
    align="center",
)

navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.A(
                        html.Img(src=app.get_asset_url("plotly-dash-icon.png"), height="30px"),
                        href="https://plot.ly",
                        target="_blank"
                    )
                ),
                dbc.Col(
                    html.A(
                        "austintexas.gov", href="https://www.austintexas.gov/", target="_blank",
                        className="ms-5",
                        style={'color': '#EEEEEE', 'font-size': '18px', 'font-weight': 'bold'}
                    )
                ),
            ],
            align="center",
            className="ms-1"
        ),
        dbc.Collapse(sm_bar, id="navbar-collapse", navbar=True)
    ],
    sticky="top",
    color="dark"
    #color="#00204E",
    #dark=True,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, navbar, content])

# homepage content
home_page = html.Div([
    dbc.Row([
        dbc.Col([
            de.Lottie(options=options, width="80%", height="80%", url=app.get_asset_url("lottie-cat-homepage.json"))
        ], width={'size':4}),
        dbc.Col([
            html.H1("Dash Summer Challenge", className="text-center font-weight-bold", title="Austin Animal Center | Austin Texas Government", style={'font-size':'120px'})
        ], width={'size':8})
    ], justify="center", align="center", className="g-0"),

    html.Hr(),

    dbc.Row([
        dbc.Col([], width=1),
        dbc.Col([
            html.H6("This application was developed for the Dash Summer Challenge, using the dataset provided by the Austin Animal Shelter. It contains " +
                "statistics and outcomes of cats entering the Austin Animal Shelter System. The goal is to help the people working at this shelter " +
                "understand their data better and allow for higher adoption rates.")
        ], width=10),
        dbc.Col([], width=1),
    ]),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Alert(["Developed and maintained by - ", html.A("Deepa Shalini Kalakonda",
                href="https://www.linkedin.com/in/deepa-shalini-273385193/", target="_blank")],
                color="dark", className="font-weight-bold")
        ], width={'size': 12})
    ])
])

@app.callback(Output("page-content", "children"),
            [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return home_page
    elif pathname == "/outcomes-overview":
        return outcomes_overview.layout
    elif pathname == "/outcomes-subtypes-overview":
        return outcome_subtypes_overview.layout
    elif pathname == "/distributions":
        return distributions.layout
    elif pathname == "/outcomes-by-age":
        return outcomes_by_age.layout
    elif pathname == "/outcomes-by-breed":
        return outcomes_by_breed.layout
    # If the user tries to reach a different page, returns a 404 message
    return de.Lottie(options=options, width='50%', height='50%', url=app.get_asset_url("lottie-cat-404.json"))

if __name__ == '__main__':
    app.run_server(debug=False)
