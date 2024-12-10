import dash
from dash import html, dcc, callback, Output, Input, State
import pandas as pd
from .raw_data import get_DataFrame

# Register the page
dash.register_page(__name__, path="/status")

# Load and prepare data
df = get_DataFrame()
df['Date'] = pd.to_datetime(df['Date'])
df = df[df['Canton'].notna() & df['Reserve_Status'].notna()]

# Prepare date slider marks
available_dates = sorted(df['Date'].dt.date.unique())
oldest_date_index = 0
latest_date_index = len(available_dates) - 1
current_date_index = latest_date_index
date_marks = {
    oldest_date_index: available_dates[oldest_date_index].strftime('%d.%m.%Y'),
    latest_date_index: available_dates[latest_date_index].strftime('%d.%m.%Y')
}

# Map Reserve_Status to images
status_images = {
    "Extremely Critical": "/assets/stand_1.svg",
    "Critical": "/assets/stand_2.svg",
    "Low": "/assets/stand_3.svg",
    "Normal": "/assets/stand_4.svg",
    "High": "/assets/stand_5.svg",
}

# Layout for the status page
layout = html.Div([
    html.H1('Blood Group Reserve Status', className='H1'),

    html.Div([
        html.Div([
            html.H4('Please select a date:', className='H4'),
            dcc.Slider(
                id='date-slider',
                min=oldest_date_index,
                max=latest_date_index,
                value=current_date_index,
                marks=date_marks,
                step=1,
                tooltip={'placement': 'bottom', "always_visible": False}
            ),
            html.H4('Please select a canton:', className='H4'),
            dcc.Dropdown(
                id='canton-dropdown-status',
                options=[{'label': c, 'value': c} for c in df['Canton'].unique()],
                value=None,
                multi=False
            ),
            html.Button("Show Legend", id="open-modal-btn", className="modal_status_legend-toggle-button")
        ], className='flex-left'),

        # Container for title and images
        html.Div(
            id="status-images",
            className='flex-right',
            style={
                'display': 'flex', 
                'flexDirection': 'column', 
                'alignItems': 'center', 
                'justifyContent': 'flex-start'
            }
        )
    ], className='flex-container'),

    # Modal container
    html.Div(
        id="legend-modal",
        className="modal_status_legend",
        style={"display": "none"},
        children=[
            html.Div(
                className="modal-content",
                children=[
                    html.Span("×", id="close-modal-btn", className="close-button"),
                    html.H3("Legend for Blood Reserve"),
                    html.Ul([
                        html.Li([html.Strong("High"), ": sufficient for more than 10 days"]),
                        html.Li([html.Strong("Normal"), ": lasts for 6 - 10 days"]),
                        html.Li([html.Strong("Low"), ": lasts for 4 - 6 days"]),
                        html.Li([html.Strong("Critical"), ": lasts for 2 - 4 days"]),
                        html.Li([html.Strong("Extremely Critical"), ": lasts less than 2 days"]),
                    ]),
                ]
            )
        ]
    ),
])

# Callback to set default canton from the stored selection
@callback(
    Output('canton-dropdown-status', 'value'),
    Input('selected-canton-store', 'data')
)
def set_default_canton(canton):
    return canton if canton else df['Canton'].unique()[0]

# Callback for dynamically updating images
@callback(
    Output("status-images", "children"),
    [Input("date-slider", "value"),
     Input("canton-dropdown-status", "value")]
)
def update_reserve_status_images(selected_date_index, selected_canton):
    selected_date = available_dates[selected_date_index]

    filtered_df = df[
        (df['Date'].dt.date == selected_date) &
        (df['Canton'] == selected_canton)
    ]

    if filtered_df.empty:
        return [html.P("Please select a canton and a date.", style={'textAlign': 'center'})]

    # Construct the title with only date and canton in bold
    title_element = html.P([
        "Blood reserves from ",
        html.B(selected_date.strftime('%d.%m.%Y')),
        " for ",
        html.B(selected_canton)
    ], className='title_element')

    image_elements = [
        html.Div([
            html.Img(src=status_images[status], style={'height': '120px', 'margin': '5px'}),
            html.P(f"{blood_type} ({status})", style={'textAlign': 'center', 'fontSize': '14px'})
        ], style={'width': '150px', 'textAlign': 'center', 'margin': '5px'})
        for blood_type, status in zip(filtered_df['Blood_Type'], filtered_df['Reserve_Status'])
        if status in status_images
    ]

    return [
        title_element,
        html.Div(
            image_elements,
            style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}
        )
    ]

# Callback to toggle modal visibility
@callback(
    Output("legend-modal", "style"),
    [Input("open-modal-btn", "n_clicks"),
     Input("close-modal-btn", "n_clicks")],
    [State("legend-modal", "style")]
)
def toggle_modal(open_clicks, close_clicks, current_style):
    if open_clicks or close_clicks:
        if current_style["display"] == "none":
            return {"display": "block"}
        return {"display": "none"}
    return current_style
