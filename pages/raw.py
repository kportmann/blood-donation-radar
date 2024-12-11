import dash
from dash import html, dcc, callback, Input, Output, dash_table
import pandas as pd
import os

# Register the page (if using Dash multipage app framework)
dash.register_page(__name__)

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
            # Add the DataTable
            dash_table.DataTable(
                id='data-table',
                columns=[
                    {"name": col, "id": col} for col in data.columns
                ],  # Dynamically create columns from the DataFrame
                data=data.to_dict('records'),  # Convert DataFrame to dictionary for Dash
                style_table={'overflowX': 'auto'},  # Enable horizontal scrolling
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'fontFamily': 'Arial, sans-serif',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                page_size=10,  # Show 10 rows per page
                filter_action="native",  # Enable filtering
                sort_action="native",  # Enable sorting
                page_action="native",  # Enable paging
                export_format=None,
            ),
            # Export button
            html.Div(
                children=[
                    html.Button("Export to CSV", id="export-button", className="export-button")
                ],
                className="export-container"
            )
        ],
        className="data-table-container"
    ),
    # Hidden Div for exporting the data
    dcc.Download(id="download-dataframe-csv")
])

# Callback für Export-Funktion
@dash.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    prevent_initial_call=True
)
def export_to_csv(n_clicks):
    return dcc.send_data_frame(data.to_csv, "exported_data.csv")
