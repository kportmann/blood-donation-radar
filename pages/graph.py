import dash
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from .raw_data import get_DataFrame

# Register the page
dash.register_page(__name__, path="/graph")

# Load and prepare data
df = get_DataFrame()

# Convert 'Date' to datetime and filter missing values
df['Date'] = pd.to_datetime(df['Date'])
df = df[df['Canton'].notna() & df['Demand_in_Liter'].notna()]

# Prepare date range slider marks
available_dates = sorted(df['Date'].dt.date.unique())
date_indices = {
    i: date.strftime('%b %Y') for i, date in enumerate(available_dates) if date.day <= 7 and (date.month in [6, 12])
}
min_date_index = 0
max_date_index = len(available_dates) - 1

# Layout for the timeline page
layout = html.Div([
    html.H1('Days until Blood-Shortage', className='H1'),

    # Flex container for filters and graph
    html.Div([
        # Left column: Filters
        html.Div([
            html.H4('Select Date Range:', className='H4'),
            dcc.RangeSlider(
                id='date-range-slider',
                min=min_date_index,
                max=max_date_index,
                value=[min_date_index, max_date_index],
                marks=date_indices,
                step=1,
                tooltip={'placement': 'bottom', 'always_visible': False},
            ),
            html.H4('Select Cantons:', className='H4'),
            dcc.Dropdown(
                id="canton-dropdown-graph",
                options=[{'label': c, 'value': c} for c in df['Canton'].unique()],
                value=None,
                multi=True,
            ),
            html.H4('Select Blood Types:', className='H4'),
            dcc.Dropdown(
                id="blood-type-dropdown-graph",
                options=[{'label': b, 'value': b} for b in df['Blood_Type'].unique()],
                value=None,
                multi=True,
            ),
            html.Button("Show Legend", id="open-modal-btn", className="modal_status_legend-toggle-button"),
        ], className='flex-left'),

        # Right column: Single Graph
        html.Div([
            dcc.Graph(id="combined-graph", style={'height': '100%', 'width': '100%'}),
        ], className='flex-right'),
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
                    html.H3("Legend for Graph"),
                    html.Ul([
                        html.Li([
                            "How many days is the Bloodreserve sufficient at specific date",
                            html.Ul([
                                html.Li([html.Strong("Recomendation"), ": if you are displaying more than 2 blood types, consider to focus on smaller timeperiods, otherwise the dashboard will be cluttered."]),
                                html.Li([html.Strong("darker colors", style={'color': '#4f4f4f'}), ": positive Bloodtypes"]),
                                html.Li([html.Strong("lighter colors", style={'color': '#828282'}), ": negative Bloodtypes"]),
                                html.Li([html.Strong("Shortage", style={'color': '#ed8a8a'}), ": <4 days"])
                            ])
                        ])
                    ])
                ]
            )
        ]
    ),
])

# Callback to set default canton from the stored selection
@callback(
    Output('canton-dropdown-graph', 'value'),
    Input('selected-canton-store', 'data')
)
def set_default_canton(canton):
    return [canton] if canton else [df['Canton'].unique()[0]]

# Callback to set default blood type from the stored selection
@callback(
    Output('blood-type-dropdown-graph', 'value'),
    Input('selected-blood-type-store', 'data')
)
def set_default_blood_type(blood_type):
    return [blood_type] if blood_type else [df['Blood_Type'].unique()[0]]

# Callback for the combined graph
@callback(
    Output("combined-graph", "figure"),
    [Input("canton-dropdown-graph", "value"),
     Input("blood-type-dropdown-graph", "value"),
     Input("date-range-slider", "value")]
)
def update_combined_graph(selected_cantons, selected_blood_types, selected_date_range):
    # Ensure selected_cantons and selected_blood_types are lists
    if isinstance(selected_cantons, str):
        selected_cantons = [selected_cantons]
    if isinstance(selected_blood_types, str):
        selected_blood_types = [selected_blood_types]

    # Get the selected date range from the slider
    start_date_index, end_date_index = selected_date_range
    start_date = available_dates[start_date_index]
    end_date = available_dates[end_date_index]

    # Filter the data
    filtered_df = df[
        (df['Canton'].isin(selected_cantons)) &
        (df['Blood_Type'].isin(selected_blood_types)) &
        (df['Date'].dt.date >= start_date) &
        (df['Date'].dt.date <= end_date)
    ]

    # Create an empty figure if no data is available
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title='No data available for the selected filters.')
        return empty_fig

    # Define unique colors for each blood type
    blood_type_colors = {
    "A+": "#E41A1C",   # Dark Red
    "A-": "#F48FB1",   # Light Red (Pinkish)

    "B+": "#377EB8",   # Dark Blue
    "B-": "#9ECAE1",   # Light Blue

    "0+": "#4DAF4A",   # Dark Green
    "0-": "#A1D99B",   # Light Green

    "AB+": "#FF7F00",  # Dark Orange
    "AB-": "#FDBF6F"   # Light Orange
    }

    # Create the figure for the combined blood types
    fig = go.Figure()
    for blood_type in selected_blood_types:
        blood_type_df = filtered_df[filtered_df['Blood_Type'] == blood_type]
        aggregated_df = blood_type_df.groupby('Date').mean(numeric_only=True).round(1).reset_index()

        fig.add_trace(go.Scatter(
            x=aggregated_df['Date'],
            y=aggregated_df['Enough_for_x_Days'],
            mode='lines+markers',
            name=blood_type,
            line=dict(color=blood_type_colors.get(blood_type, '#000000')),  # Default to black if color not found
            marker=dict(color=blood_type_colors.get(blood_type, '#000000'))
        ))

    # Add the threshold line
    threshold = 4
    fig.add_trace(go.Scatter(
        x=aggregated_df['Date'].unique(),
        y=[threshold] * len(aggregated_df['Date'].unique()),
        mode='lines',
        line=dict(color='#E2001A', dash='dash'),
        name='Threshold'
    ))

    # Add the critical zone
    fig.add_trace(go.Scatter(
        x=aggregated_df['Date'].tolist() + aggregated_df['Date'].tolist()[::-1],
        y=[0] * len(aggregated_df) + [threshold] * len(aggregated_df),
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',
        line=dict(width=0),
        showlegend=True,
        name='Critical Zone'
    ))

    # Customize layout
    fig.update_layout(
        title='<b>Blood Reserves Over Time</b>',
        xaxis_title='Date',
        yaxis_title='Days',
        hovermode='x unified',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showline=True,
                       linecolor='#cccccc',
                       linewidth=2,
                       showgrid=True,
                       gridcolor='#f5f5f5',
                       gridwidth=0.3),
        yaxis=dict(showline=True,
                        linecolor='#cccccc',
                        linewidth=2,
                        showgrid=True,
                        gridcolor='#f5f5f5',
                        gridwidth=0.3)
    )

    return fig
