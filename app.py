import os
import base64
import json
import time

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from datetime import datetime as dt
import redis
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud, STOPWORDS

import tasks
from utils.redis import REDIS_URL
from utils.getCurrentPrice import binancePriceFetch
from utils.plotly_wordcloud import plotly_wordcloud as pwc

FEEDS = ["reddit"]

# Redis
redis_instance = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
crypto_pairs = redis_instance.hgetall("cryptos_nodupe")

reverse_pairs = {}
for key, value in crypto_pairs.items():
    reverse_pairs[value] = key

redis_hashs = redis_instance.keys("*")
redis_hashs_ignore = [
    "_kombu.binding.celery",
    "_kombu.binding.celery.pidbox",
    "_kombu.binding.celeryev",
    "app-data",
    "cryptos",
    "cryptos_nodupe",
]
redis_db_pairs = [item for item in redis_hashs if "_TEXT" not in item]
redis_db_pairs = {item for item in redis_db_pairs if (item not in redis_hashs_ignore)}

# APIs
binance_client = binancePriceFetch()

# Dash
app = dash.Dash("app", external_stylesheets=[dbc.themes.JOURNAL])
server = app.server
jsonData = ''
with open('./Scraper/crypto.json') as jsonFile:
    jsonData = json.load(jsonFile)
redClient = redis.from_url(os.environ.get("REDIS_URL"))
def sidebar_content():
    crypto_meta = [html.Div(" ", id="sidebar-crypto-meta")]

    sentiment_indicator = [
        html.Div(
            [
                html.H3(f"{source.capitalize()}:" if source != "des" else "Overall:"),
                html.Div(" ", id=f"sidebar-sentiment-{source}"),
            ]
        )
        for source in FEEDS + ["des"]
    ]

    contents = crypto_meta + sentiment_indicator
    return html.Div(contents)


def sidebar():
    sidebar_header = dbc.Row([dbc.Col(html.H3("Overall Sentiment"))])
    sidebar_contents = html.Div(
        children=[
            html.Div(
                [
                    dcc.Dropdown(
                        id="sidebar-sentiment-dropdown",
                        options=[
                            {"label": coin, "value": symbol}
                            for coin, symbol in crypto_pairs.items()
                        ],
                        value="BTC",
                        placeholder="Select Cryptocurrency",
                    ),
                ]
            ),
            html.Br(),
            sidebar_content(),
        ]
    )

    sidebar = html.Div(
        id="sidebar", children=[sidebar_header, html.Hr(), sidebar_contents],
    )
    return sidebar


def main_container(id="", header_name="header", short_desc="", value="BTC"):
    dropdowns = html.Div(
        [
            html.H4(header_name, id=header_name),
            html.P(short_desc),
            html.Hr(),
            html.Div(
                [
                    dcc.Dropdown(
                        id=f"main-{id}-dropdown",
                        options=[
                            {"label": coin, "value": coin} for coin in redis_db_pairs
                        ],
                        multi=True,
                        value=value,
                        placeholder="Select Cryptocurrency",
                    ),
                ],
                style={"width": "50%"},
            ),
        ]
    )

    graph_container = dbc.Row(id=f"main-{id}-container", children=[])

    container = html.Div([dropdowns, graph_container], style={"padding": "25px"})
    return container


def header():
    nav = dbc.Navbar(
        color="dark",
        dark=True,
        className="app-header-container",
        children=[
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(src="./assets/logo.png", height="45px"),
                        className="col-1 app-header-logo",
                    ),
                    dbc.Col(
                        dbc.NavbarBrand("CryptoHub", className="col-9 app-header-title")
                    ),
                    dbc.Col(
                        children=[
                            dbc.Button(
                                "≡",
                                id="sidebar-toggle-button",
                                outline=True,
                                color="warning",
                                n_clicks=0,
                            ),
                        ],
                        className="mr-1 sidebar-toggle-button",
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                id="navbar-collapse",
                navbar=True,
                children=[
                    # dbc.Row(
                    #     dbc.Col(dbc.NavLink("Home", href="#")),
                    #     no_gutters=True,
                    #     className="ml-auto flex-nowrap mt-3 mt-md-0",
                    #     align="center",
                    # ),
                ],
            ),
        ],
    )
    return nav


def serve_layout():
    return html.Div(
        [
            header(),
            html.Div(
                [
                    dbc.Row(
                        children=[
                            html.Div(
                                id="sidebar-container",
                                className="sidebar-container-show",
                                children=[sidebar()],
                            ),
                            html.Div(
                                id="app-container",
                                children=[
                                    main_container(
                                        id="sentiment-agg",
                                        header_name="Sentiment",
                                        short_desc="A visualization of sentiment counts.",
                                        value="BITCOIN",
                                    ),
                                    main_container(
                                        id="wordmaps",
                                        header_name="Wordmaps",
                                        short_desc="A visualization of word counts.",
                                        value="BITCOIN",
                                    ),
                                ],
                                className="app-contents-container",
                            ),
                        ],
                        className="row-margin-zero",
                    ),
                ],
                className="app-contents",
            ),
            dcc.Interval(interval=5 * 1000, id="interval"),
        ]
    )


app.layout = serve_layout

# CSS Callbacks
# -------------------------------------------------------------------
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [Output("sidebar", "className"), Output("app-container", "className")],
    [Input("sidebar-toggle-button", "n_clicks")],
)
def toggle_sidebar_collapse(n):
    if n % 2 == 0:
        return "sidebar-container-show", "app-contents-container"
    return "sidebar-container-hide", "app-contents-container-full"


@app.callback(
    [
        Output(f"sidebar-sentiment-{provider}", "children")
        for provider in FEEDS + ["des"]
    ]
    + [
        Output(f"sidebar-sentiment-{provider}", "className")
        for provider in FEEDS + ["des"]
    ],
    [Input("sidebar-sentiment-dropdown", "value")],
)
def update_sidebar_sentiment(selected_crypto):
    data = redClient.lrange(jsonData[selected_crypto].upper(), 0, 0)
    text =0
    for entry in data:
        text = text + json.loads(entry.decode('UTF-8'))['avg_sentiment']


    return ["%.2f" % (text*100) for i in range(len(FEEDS) + 1)] + [
        "sidebar-container-sentiment-negative" for i in range(len(FEEDS) + 1)]


# Callbacks
# -------------------------------------------------------------------
@app.callback(
    Output("sidebar-crypto-meta", "children"),
    [Input("sidebar-sentiment-dropdown", "value"), Input("interval", "n_intervals")],
)
def update_sidebar_crypto_meta(selected_crypto, _):
    try:
        price = binance_client.getPrice(selected_crypto)
        curr_time = time.asctime(time.localtime(time.time()))

        formatted_meta = html.Div(
            [
                html.Div(
                    [html.B("Price (Binance):"), html.P(f"{round(float(price), 2)}"),]
                ),
                html.Div([html.B("Time:"), html.P(f"{curr_time}")]),
            ],
        )
    except:
        formatted_meta = html.Div(
            [
                html.B("Error:"),
                html.P(
                    "Selected Coin not listed on Binance. (Try a popular coin like Bitcoin, or Ethereum)"
                ),
            ]
        )

    return formatted_meta


@app.callback(
    Output("main-wordmaps-container", "children"),
    [Input("main-wordmaps-dropdown", "value")],
    [State("main-wordmaps-container", "children")],
)
def render_dynamic_wordmaps(selected_cryptos, container):
    if not isinstance(selected_cryptos, list):
        selected_cryptos = [selected_cryptos]

    container_len = len(container)
    cryptos_len = len(selected_cryptos)

    if cryptos_len == 0:
        return []

    if cryptos_len > container_len:
        container = []
        for crypto in selected_cryptos:
            text = redis_instance.lrange(crypto + "_TEXT", 0, -1)
            text = [json.loads(itm) for itm in text]

            df_text = pd.DataFrame(text)
            text = df_text.loc[0, "text"]
            fig = pwc(text)
            col_graph = dbc.Col(dcc.Graph(figure=fig), width=6)
            container.append(col_graph)
    elif cryptos_len < container_len:
        container.pop()
    return container


@app.callback(
    Output("main-sentiment-agg-container", "children"),
    [Input("main-sentiment-agg-dropdown", "value")],
    [State("main-sentiment-agg-container", "children")],
)
def render_dynamic_sentiments(selected_cryptos, container):
    if not isinstance(selected_cryptos, list):
        selected_cryptos = [selected_cryptos]

    container_len = len(container)
    cryptos_len = len(selected_cryptos)

    if cryptos_len == 0:
        return []

    if cryptos_len > container_len:
        container = []

        for crypto in selected_cryptos:
            meta = redis_instance.lrange(crypto, 0, -1)
            meta = [json.loads(itm) for itm in meta]

            df_meta = pd.DataFrame(meta)

            fig = px.bar(
                df_meta,
                x="date",
                y="avg_sentiment",
                hover_data=["samples"],
                labels={"avg_sentiment": "Average Sentiment"},
            )
            fig.update_layout(title=f"{crypto}")
            sentiment_text_container = html.Div(
                children=[
                    html.Br(),
                    html.H5("Text"),
                    html.Hr(),
                    html.P("Click on a point to see text data..."),
                    html.Div(id=f"main-sentiment-{crypto}-text", children=[]),
                ]
            )

            col_graph = dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col([dcc.Graph(figure=fig)], width=12),
                        ]
                    )
                ],
                width=6,
            )
            container.append(col_graph)
    elif cryptos_len < container_len:
        container.pop()
    return container

if __name__ == "__main__":
    app.run_server(debug=True)
