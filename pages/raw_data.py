import dash
from dash import html, dcc, callback, Input, Output, dash_table
import pandas as pd
import os

# Register the page (if using Dash multipage app framework)
dash.register_page(__name__, path="/raw_data", name="Data")

# Get the directory of the current file (raw.py)
current_dir = os.path.dirname(__file__)

# Construct the relative path to the CSV file in the data folder
csv_path = os.path.join(current_dir, "../data/blood_reserve_data.csv")

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_path)

## Relevant to get the data the way we need it.
def get_DataFrame():
    # Load the data
    df = pd.read_csv(csv_path)

    # Calculate mean values grouped by Canton and Blood_Type, dividing by 7
    mean_df = ((df.groupby(['Canton', 'Blood_Type'])['Demand_in_Liter'].mean() / 7).round(2)).reset_index()

    # Rename column in mean_df for clarity
    mean_df.rename(columns={'Demand_in_Liter': 'Mean_Demand_Per_Day'}, inplace=True)

    # Merge the mean_df back into the original df for proper alignment
    df = df.merge(mean_df, on=['Canton', 'Blood_Type'])

    # Calculate the 'Enough_for_x_Days' column
    df['Enough_for_x_Days'] = (df['Blood_in_Liter'] / df['Mean_Demand_Per_Day']).round(2)

    # Define classify function
    def classify_blood_reserve(B):
        if B > 10:
            return "High"
        elif B <= 10 and B > 6:
            return "Normal"
        elif B <= 6 and B > 4:
            return "Low"
        elif B <= 4 and B > 2:
            return "Critical"
        elif B <= 2:
            return "Extremely Critical"
        else:
            return "No Blood Available"

    # Apply the classification function to the Enough_for_x_Days column
    df['Reserve_Status'] = df['Enough_for_x_Days'].apply(classify_blood_reserve)
    return df

# Prepare the processed DataFrame
data = get_DataFrame()

# Layout for the data table
layout = html.Div([
    html.H1("Raw Data Overview"),

    # DataTable container
    html.Div(
        children=[
            dash_table.DataTable(
                id='data-table',
                columns=[
                    {"name": col, "id": col} for col in data.columns
                ],
                data=data.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'fontFamily': 'Arial, sans-serif',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                page_size=10,
                filter_action="native",
                sort_action="native",
                page_action="native",
                export_format="csv",
                export_headers="display",
            ),
            html.Button("Show Legend", id="open-modal-btn", className="modal-toggle-button"),
        ],
        className="data-table-container"
    ),
    
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
                    html.H3("Legend for Data Table"),
                    html.Ul([
                        html.Li([html.Strong("Blood_in_Liter"), ": Blood Reserve per Bloodtype/Day/Canton (Liters)."]),
                        html.Li([html.Strong("Demand_in_Liter"),": Demanded Blood per Bloodtype/Day/Canton (Liters)."]),
                        html.Li([html.Strong("Mean_Demand_Per_Day"),": Mean Demand per Bloodtype/Day/Canton (Liters) calculated over whole Period."]),
                        html.Li([html.Strong("Enough_for_x_Days"),": Shows how long Blood will last = Blood_in_Liter : Mean_Demand_Per_Day."]),
                        html.Li([
                            html.Strong("Reserve_Status:"),
                            html.Ul([
                                html.Li([html.Strong("High"),": sufficient for more than 10 days"]),
                                html.Li([html.Strong("Normal"),": lasts for 6 - 10 days"]),
                                html.Li([html.Strong("Low"),": lasts for 4 - 6 days"]),
                                html.Li([html.Strong("Critical"),": lasts for 2 - 4 days"]),
                                html.Li([html.Strong("Extremely Critical"),": lasts less than 2 days"]),
                            ])
                        ]),
                    ])
                ]
            )
        ]
    ),
])


