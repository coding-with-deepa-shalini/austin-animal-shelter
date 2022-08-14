import os
import dash
from dash import dcc, html
import dash_extensions as de
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# default bootstrap theme
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
)

# content from pages
content = html.Div(dash.page_container, style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, navbar, content])

if __name__ == "__main__":
    app.run(debug=False)
