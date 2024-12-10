import dash
from dash import html, dcc, callback, Input, Output
from dash.dependencies import Input, Output
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
    i: date.strftime('%b %Y')  # Display only the month
    for i, date in enumerate(available_dates)
    if date.day <= 7 and (date.month in [6, 12])
}
min_date_index = 0
max_date_index = len(available_dates) - 1

# Layout for the timeline page
layout = html.Div([
    html.H1('Days until Blood-Shortage', className='H1'),

    # Flex container for filters and graph
    html.Div([
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
                value=None,#[df['Canton'].unique()[2]],  # 2 = LU
                multi=True,
            ),
            html.Button("Show Legend", id="open-modal-btn", className="modal_status_legend-toggle-button"),
        ], className='flex-left'),

        # Right column: Graphs
        html.Div([
            dcc.Graph(id="graph-A", style={'height': '50%', 'width': '100%'}),
            dcc.Graph(id="graph-B", style={'height': '50%', 'width': '100%'}),
            dcc.Graph(id="graph-O", style={'height': '50%', 'width': '100%'}),
            dcc.Graph(id="graph-AB", style={'height': '50%', 'width': '100%'}),
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
                                html.Li([html.Strong("blue", style={'color': 'blue'}), ": positive Bloodtypes"]),
                                html.Li([html.Strong("red", style={'color': 'red'}), ": negative Bloodtypes"]),
                                html.Li([html.Strong("Shortage", style={'color': 'pink'}), ": <4 days"])
                            ])
                        ])
                    ])
                ]
            )
        ]
    ),
])

@callback(
    Output('canton-dropdown-graph', 'value'),
    Input('selected-canton-store', 'data')
)
def set_default_canton(canton):
    return canton if canton else df['Canton'].unique()[0]

# Callback for the graphs
@dash.callback(
    [Output("graph-A", "figure"),
     Output("graph-B", "figure"),
     Output("graph-O", "figure"),
     Output("graph-AB", "figure")],
    [Input("canton-dropdown-graph", "value"),
     Input("date-range-slider", "value")]
)
def update_graphs(selected_cantons, selected_date_range):
    if isinstance(selected_cantons, str):
        selected_cantons = [selected_cantons]

    # Get the selected date range from the slider
    start_date_index, end_date_index = selected_date_range
    start_date = available_dates[start_date_index]
    end_date = available_dates[end_date_index]

    # Filter the data
    filtered_df = df[
        (df['Canton'].isin(selected_cantons)) &
        (df['Date'].dt.date >= start_date) &
        (df['Date'].dt.date <= end_date)
    ]

    # Check if filtered data is empty
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title='No data available for the selected filters.',
        )
        return empty_fig, empty_fig, empty_fig, empty_fig

    # Define blood type groups
    blood_type_groups = {
        "A": ["A+", "A-"],
        "B": ["B+", "B-"],
        "0": ["0+", "0-"],
        "AB": ["AB+", "AB-"]
    }

    figures = []
    for group, subtypes in blood_type_groups.items():
        # Filter by blood type group
        group_df = filtered_df[filtered_df['Blood_Type'].isin(subtypes)]

        # Aggregate data by date and blood type
        aggregated_df = (group_df.groupby(['Date', 'Blood_Type']).mean(numeric_only=True)).round(1).reset_index()

        # Create the figure for the group
        fig = go.Figure()
        for subtype in subtypes:
            subtype_df = aggregated_df[aggregated_df['Blood_Type'] == subtype]
            fig.add_trace(go.Scatter(
                x=subtype_df['Date'],
                y=subtype_df['Enough_for_x_Days'],
                mode='lines+markers',
                name=subtype,
                #line=dict(color='black' if '+' in subtype else '#FF6961')
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
            fillcolor='rgba(2550, 0, 0, 0.2)',
            line=dict(width=0),
            showlegend=True,
            name='Critical Zone'
        ))

        # Customize layout
        fig.update_layout(
            title=f'<b>Blood Types: {group} +- </b>',
            xaxis_title='Date',
            yaxis_title='Days',
            hovermode='x unified',
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showline=True,
                       linecolor='#cccccc',
                       linewidth=2,
                       showgrid=True,
                       gridcolor='lightgrey',
                       gridwidth=0.5),
            yaxis=dict(showline=True,
                        linecolor='#cccccc',
                        linewidth=2,
                        showgrid=True,
                        gridcolor='lightgrey',
                        gridwidth=0.5),
        )
        figures.append(fig)

    return figures[0], figures[1], figures[2], figures[3]
