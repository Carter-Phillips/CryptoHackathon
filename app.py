import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import flask
import json
import redis
import time
import os
import pandas as pd

import tasks
from utils.redis import REDIS_URL

app = dash.Dash("app")
server = app.server

# Heroku
redis_instance = redis.StrictRedis.from_url(REDIS_URL)

# Google
# redis_instance = redis.Redis(host=GOOGLE_REDIS_HOST, port=GOOGLE_REDIS_PORT)

print(redis_instance)
def serve_layout():
    return html.Div(
        [
            dcc.Interval(interval=5 * 1000, id="interval"),
            html.H1("Redis, Celery, and Periodic Updates"),
            html.Div(id="status"),
            dcc.Dropdown(
                id="dropdown",
                options=[{"value": i, "label": i} for i in ["LA", "NYC", "MTL"]],
                value="LA",
            ),
            dcc.Graph(id="graph"),
        ]
    )


app.layout = serve_layout


def get_dataframe():
    """Retrieve the dataframe from Redis
    This dataframe is periodically updated through the redis task
    """
    jsonified_df = redis_instance.hget(
        tasks.REDIS_HASH_NAME, tasks.REDIS_KEYS["DATASET"]
    ).decode("utf-8")
    df = pd.DataFrame(json.loads(jsonified_df))
    return df


@app.callback(
    Output("graph", "figure"),
    [Input("dropdown", "value"), Input("interval", "n_intervals")],
)
def update_graph(value, _):
    df = get_dataframe()
    return {
        "data": [{"x": df["time"], "y": df["value"], "type": "bar"}],
        "layout": {"title": value},
    }


@app.callback(
    Output("status", "children"),
    [Input("dropdown", "value"), Input("interval", "n_intervals")],
)
def update_status(value, _):
    data_last_updated = redis_instance.hget(
        tasks.REDIS_HASH_NAME, tasks.REDIS_KEYS["DATE_UPDATED"]
    ).decode("utf-8")
    return "Data last updated at {}".format(data_last_updated)


if __name__ == "__main__":
    app.run_server(debug=True)
