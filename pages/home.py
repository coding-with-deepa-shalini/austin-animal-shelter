import dash
from dash import dcc, html
import dash_extensions as de
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

dash.register_page(
    __name__,
    path='/',
    title="Austin Animal Shelter",
    name="Home"
)

options = dict(loop=True, autoplay=True) #rendererSettings=dict(preserveAspectRatio='xMidYmid slice'

layout = html.Div([
    dbc.Row([
        dbc.Col([
            de.Lottie(options=options, width="80%", height="80%", url="assets/lottie-cat-homepage.json")
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
