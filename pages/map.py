import dash
import plotly.graph_objects as go
import json
import pandas as pd
import os
from dash import dcc, html, callback
from datetime import datetime
from dash.dependencies import Input, Output
from .raw_data import get_DataFrame

# Load GeoJSON data for Switzerland's map
current_dir = os.path.dirname(__file__)
project_dir = os.path.abspath(os.path.join(current_dir, '..'))
data_dir = os.path.join(project_dir, 'data')
geojson_path = os.path.join(data_dir, 'switzerland.geojson')

with open(geojson_path) as f:
    geojson_data = json.load(f)

# Load and prepare the data
df = get_DataFrame()
df['Date'] = pd.to_datetime(df['Date'])  # Convert 'Date' column to datetime
available_dates = sorted(df['Date'].dt.date.unique())  # Get unique dates sorted
oldest_date_index = 0
latest_date_index = len(available_dates) - 1
current_date = datetime.now().date()

# Create slider marks with only min and max dates
date_marks = {
    oldest_date_index: available_dates[oldest_date_index].strftime('%d.%m.%Y'),
    latest_date_index: available_dates[latest_date_index].strftime('%d.%m.%Y')
}

# Register the Dash page
dash.register_page(__name__, path='/')

# Define the layout of the app
layout = html.Div([
    html.H1('Map view - Switzerland', className='h1'),

    # Flex container for menu and content
    html.Div([
        html.Div([
            html.H4('Please select a date:', className='h4'),
            dcc.Slider(
                id='date-slider',
                min=oldest_date_index,
                max=latest_date_index,
                value=latest_date_index,
                marks=date_marks,
                step=1,
                tooltip={'placement': 'bottom', "always_visible": False}
            ),
            html.H4('Please select a blood type:', className='h4'),
            dcc.Dropdown(
                id='blood-type-dropdown',
                options=[{'label': b, 'value': b} for b in df['Blood_Type'].unique()],
                value=None, #df['Blood_Type'].unique()[0],  # Default selection
                multi=False
            ),
            html.Button("Show Legend", id="open-modal-btn", className="modal_status_legend-toggle-button"),  #Button for Legend
        ], className='flex-left'),

        # Right column: Choropleth map
        html.Div([
            dcc.Graph(
                id='choropleth-map',
                style={'height': '100%', 'width': '100%'}
            ),
            html.P('Hover over the map for exact Values.', style={'textAlign': 'right', 'font-size': '10px'}),
        ], className='flex-right')
    ], className='flex-container'),

    # Modal container for the legend
    html.Div(
        id="legend-modal",
        className="modal_status_legend",
        style={"display": "none"},
        children=[
            html.Div(
                className="modal-content",
                children=[
                    html.Span("×", id="close-modal-btn", className="close-button"),
                    html.H3("Color-Legend"),
                    html.Ul([
                        html.Li([html.Strong("green", style={'color': 'green'}),": >10 days (Status: High)"]),
                        html.Li([html.Strong("lightgreen", style={'color': 'lightgreen'}),": 6-10 days (Status: Normal)"]),
                        html.Li([html.Strong("yellow/orange", style={'color': 'orange'}),": 4-6 days (Status: Low)"]),
                        html.Li([html.Strong("red", style={'color': 'red'}),": 2-4 days (Status: Critical)"]),
                        html.Li([html.Strong("darkred", style={'color': 'darkred'}),": <2 days (Status: Extremely Critical)"]),
                    ])
                ]
            )
        ]
    ),
])

# Callback to set default values from the stored selection
@callback(
    Output('blood-type-dropdown', 'value'),
    Input('selected-blood-type-store', 'data')
)
def set_default_blood_type(blood_type):
    return blood_type if blood_type else df['Blood_Type'].unique()[0]

# Callback to update the Choropleth map based on the selected date and blood type
@callback(
    Output('choropleth-map', 'figure'),
    [Input('date-slider', 'value'),
     Input('blood-type-dropdown', 'value')]
)
def update_choropleth(selected_date_index, selected_blood_type):
    # Filter data for the selected date and blood type
    selected_date = available_dates[selected_date_index]
    filtered_df = df[(df['Date'].dt.date == selected_date) & (df['Blood_Type'] == selected_blood_type)]

    # Create a Choropleth map with permanent labels
    fig = go.Figure(go.Choropleth(
        geojson=geojson_data,
        locations=filtered_df['Canton'],
        z=filtered_df['Enough_for_x_Days'],
        featureidkey="properties.name",
        text=filtered_df['Enough_for_x_Days'].astype(str) + " Days",
        hoverinfo="location+z",
        colorscale=[
            [0, "darkred"],
            [0.1, "red"],
            [0.3, "yellow"],
            [0.5, "green"],
            [1, "darkgreen"]
        ],
        zmin=2,
        zmax=20,
        colorbar_title="Days"
    ))

    # Update layout to center the map and add text
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(marker_line_width=0.5, marker_line_color="black")
    fig.update_layout(
        title={
            'text': (
                f'Blood reserves from <b>{selected_date.strftime("%d.%m.%Y")}</b> '
                f'for <b>{selected_blood_type}</b>'
            ),
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(size=12),
    )
    return fig