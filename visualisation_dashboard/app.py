# Import required libraries
import pickle
import copy
import pathlib
import urllib.request
import dash
import math
import os
import numpy as np
import plotly.express as px
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_gif_component as gif
import dash_html_components as html
import plotly.graph_objects as go
# Multi-dropdown options
from controls import HALO_STATUS
# halo_options = ['HH', 'FH', 'PH']
from load_dfs import load_dataframes

df = load_dataframes()

columns = []
for i in range(len(df.columns)): 
    columns.append(df.columns[i][0])

df.columns = columns

Halo_options = df['LASCO_halo'].unique()

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "P-DBM database, Napolitano et al. 2021"
server = app.server


# Create controls
# county_options = [
#     {"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES
# ]

# Halo_options = [
#     {"label": str(HALO_STATUS[well_status]), "value": str(well_status)}
#     for well_status in HALO_STATUS
# ]

cme_types= [
    {"label": str(HALO_STATUS[cme_type]), "value": str(cme_type)}
    for cme_type in HALO_STATUS
]



print(cme_types)

# cme_types = Halo_options

df["LASCO_Start"] = pd.to_datetime(df["LASCO_Start"])
df = df[pd.to_datetime(df["LASCO_Start"]) > dt.datetime(1990, 1, 1)]


years = pd.DatetimeIndex(df['LASCO_Start']).year.unique()


# trim = df[["CME_num", "LASCO_halo", "DST"]]
# trim.index = trim["CME_num"]
# dataset = trim.to_dict(orient="index")




# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [    gif.GifPlayer(
                                gif='../data/dash-logo.gif',
                                still='../data/dash-logo.jpg',
                            )
                        # html.Img(
                        #     src=("../data/dash-logo.png"),#'https://www.esa.int/ESA_Multimedia/Images/2020/10/New_view_of_2012_solar_activity_gif', #app.get_asset_url("../data/dash-logo.png"),
                        #     id="plotly-image",
                        #     style={
                        #         "height": "60%",
                        #         "width": "60%",
                        #         "margin-bottom": "25px",
                        #     },
                        # )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "P-DBM CME database",
                                    style={"margin-bottom": "2px"},
                                ),
                                html.H5(
                                    "Napolitano et al. 2021", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Img(
                                src='https://projectescape.eu/sites/default/files/logo-Escape_0.png',
                                style={
                                    'height' : '60%',
                                    'width' : '60%',
                                    'float' : 'right',
                                    'position' : 'relative',
                                    'padding-top' : 0,
                                    'padding-right' : 0
                                })
                            # href="https://projectescape.eu/sites/default/files/logo-Escape_0.png",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Filter by CME date (or select range in histogram):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            marks = {i: '{}'.format(i) for i in range(years.min(), years.max())},
                            min=years.min(),
                            max=years.max(),
                            value=[years.min(), years.max()],
                            className="dcc_control",
                        ),
                        html.P("Filter by HALO status:", className="control_label"
                        ),
                        dcc.Dropdown(
                            id="cme_type",
                            options=cme_types,
                            multi=True,
                            value="FH",
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [

                        html.Div(
                            [dcc.Graph(id="main_graph")],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="nine columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="TransTime_v_arr_V")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="TransTime_v_Mass")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="TransTime_v_Acc")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="bz_v_TransTime")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)



def filter_dataframe(cme_types, year_slider):
    dff = df[df["LASCO_halo"].isin(Halo_options)
    & (pd.to_datetime(df["LASCO_Start"]) > dt.datetime(year_slider[0], 1, 1))
    & (pd.to_datetime(df["LASCO_Start"]) < dt.datetime(year_slider[1], 1, 1))
    ]
    return dff





# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    #  Input("cme_types", "value"),
    [Input("main_graph", "figure")],
)





# Selectors -> main graph
@app.callback(
    Output("main_graph", "figure"),
    [
    #     Input("well_statuses", "value"),
        Input("cme_type", "value"),
        # Input('submit_button', 'n_clicks'),
        Input("year_slider", "value")
    ],
    # [State("cme_types", "value"),]
)
def make_main_figure( cme_types, year_slider ):

    dff = filter_dataframe([cme_types], year_slider)
    figure = go.Figure(px.histogram(dff["LASCO_Start"] ,color = dff['LASCO_halo']))
    figure.update_layout(title="Distribution of CMEs in the database", xaxis_title="Date", yaxis_title="Frequency")
    # print(dff.shape())
    return figure


# Main graph -> individual graph
@app.callback(
    Output("TransTime_v_arr_V", "figure"), 
    [#Input("main_graph", "hoverData"),
    #     Input("well_statuses", "value"),
    Input("cme_type", "value"),
    Input("year_slider", "value"),
    ],)

def make_individual_figure( cme_types, year_slider):
    dff = filter_dataframe( cme_types, year_slider)

    figure = go.Figure(px.scatter(dff, x = 'Transit_time', y = 'Arrival_v',color = 'LASCO_halo', title = "Transit time vs Arrival speed"))
    figure.update_layout( xaxis_title="Transit time", yaxis_title="Arrival Speed")
    return figure

 

# Selectors, main graph -> aggregate graph
@app.callback(
    Output("TransTime_v_Mass", "figure"),
    [
        # Input("well_statuses", "value"),
        Input("cme_type", "value"),
        Input("year_slider", "value"),
        # Input("main_graph", "hoverData"),
    ],
)
def make_aggregate_figure( cme_types, year_slider):
    

    dff = filter_dataframe( cme_types, year_slider)

    figure = go.Figure(px.scatter(dff, x='Transit_time', y = 'Mass',color = 'LASCO_halo', log_y= True))
    figure.update_layout(title="Transit time vs Mass", xaxis_title='Transit Time', yaxis_title="Mass")
    return figure


# Selectors, main graph -> pie graph
@app.callback(
    Output("TransTime_v_Acc", "figure"),
    [
        # Input("well_statuses", "value"),
        Input("cme_type", "value"),
        Input("year_slider", "value"),
    ],
)
def make_TTvACC_figure( cme_types, year_slider):
    

    dff = filter_dataframe( cme_types, year_slider)

    figure = go.Figure(px.scatter(dff, x= 'Transit_time', y  = 'Accel.',color = 'LASCO_halo'))
    figure.update_layout(title="Transit time vs Acceleration", xaxis_title='Transit Time', yaxis_title="Acceleration")
    return figure

# Selectors -> count graph
@app.callback(
    Output("bz_v_TransTime", "figure"),
    [
        # Input("well_statuses", "value"),
        Input("cme_type", "value"),
        Input("year_slider", "value"),
    ],
)
def make_count_figure( cme_types, year_slider):

    # layout_count = copy.deepcopy(layout)
    # dff
    dff = filter_dataframe( cme_types, year_slider)
    # g = dff[["CME_num", "Bz",  "Transit_time"]]
    # g.index = g["CME_num"]
    # g = g.resample("A").count()

    colors = []
    for i in range(1990, 2021):
        if i >= int(year_slider[0]) and i < int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")

    figure  = go.Figure(px.scatter(dff, x = "Bz",  y = "Transit_time",color = 'LASCO_halo'))
    figure.update_layout(title="Transit time vs Bz( at L1)", xaxis_title='Transit Time', yaxis_title="Bz")
    
    return figure


# if __name__ == "__main__":


# # Main
# if __name__ == "__main__":
# #     app.run_server(debug=True, port = os.getenv('PORT', '8030'))
# app = dash.Dash(__name__)
# server = app.server
