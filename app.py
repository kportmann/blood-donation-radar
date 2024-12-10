import dash
from dash import Dash, html, dcc, Input, Output, State


app = Dash(__name__, use_pages=True)

from pages.raw_data import get_DataFrame
df = get_DataFrame()

app.layout = html.Div([
    html.Div(
        html.H1('Blood Donation Radar Switzerland'),
        className='header'
    ),
    html.Div(
        id="initial-modal",
        className="modal show",
        children=[
            html.Div(
                className="modal-content",
                children=[
                    html.H2("In which canton do you live and what's your Blood type?"),
                    dcc.Dropdown(
                        id="canton-selection",
                        options=[{'label': c, 'value': c} for c in df['Canton'].unique()],
                        placeholder="Select your Canton",
                    ),
                    dcc.Dropdown(
                        id="blood-type-selection",
                        options=[{'label': b, 'value': b} for b in df['Blood_Type'].unique()],
                        placeholder="Select your Bloodtype",
                    ),
                    html.Button("confirm and continue", id="confirm-selection-btn"),
                ]
            )
        ]
    ),

    # Store for selected values
    dcc.Store(id='selected-canton-store'),
    dcc.Store(id='selected-blood-type-store'),

    
    # Navigation menu
    html.Div([
        html.Div(
            [
                html.Div(
                    dcc.Link(f"{page['name']}", href=page["relative_path"]),
                    className='menu-item'
                ) 
                for page_name in ['Map', 'Status', 'Graph', 'Data'] # Define the order of the pages manually
                for page in dash.page_registry.values() if page['name'] == page_name
            ],
            className='menu-left'
        ),
        
        # GitHub Logo and Repository Link
        html.Div([
            html.A(
                html.Img(
                    src="assets/github-mark.svg",
                    alt='GitHub Logo',
                    id="github-logo",
                    style={'width': '35px', 'height':'35px'},
                ),
                href="https://github.com/kportmann/blood-donation-radar",
                target="_blank",
            ),
            html.A(
                html.Img(
                    src='assets/icons8-x-logo.svg',
                    style={'width': '35px', 'height':'35px'}),
                href='https://x.com/?lang=de',
                target='_blank'
            ),
            html.A(
                html.Img(
                    src='assets/icons8-linkedin-500.svg',
                    style={'width': '35px', 'height':'35px'}),
                href='https://www.linkedin.com',
                target='_blank'
            ),
            html.Img(
                src="/assets/question-mark.svg",
                alt='Help Icon',
                id="help-icon",
                style={'width': '35px', 'height':'35px'},
                className='help-icon'
            )
        ], className='menu-right')
    ], className='menu-container'),

    # Modal Info Box
    html.Div(
        id="modal",
        className="modal",
        children=[
            html.Div(
                className="modal-content",
                children=[
                    html.Span("✖", id="close-modal", className="close"),
                    html.H2("Welcome to the Blood Donation Radar Dashboard!"),
                    html.P("We are AI/ML students and this is our Data Visualization project for the DVIZ module."),
                    html.P([
                    "Please be aware that this is a ",
                    html.Strong("fictional project"),
                    " and the data is ",
                    html.Strong("generated"),
                    "."
                ]),
                    html.P("For more details about the dashboard functionality you can visit our gitHub Repository."),
                ]
            )
        ]
    ),
    
    # Main Content
    html.Div(
        dash.page_container,
        className='content-flexbox'
    ),
    
    # Footer Section
    html.Footer(
        html.Div([
            html.P("© 2024 Blood Donation Radar Switzerland", className='footer-text'),
            html.P("Kevin Portmann, Benjamin Amhof", className='footer-text')
        ], className='footer-content'),
        className='footer'
    )
], className='app-container')

# Callback initial modal
@app.callback(
    [Output("initial-modal", "className"),
     Output("selected-canton-store", "data"),
     Output("selected-blood-type-store", "data")],
    Input("confirm-selection-btn", "n_clicks"),
    [State("canton-selection", "value"),
     State("blood-type-selection", "value")],
    prevent_initial_call=True
)
def close_modal_and_set_defaults(n_clicks, canton, blood_type):
    return "modal", canton, blood_type


# Callback info box
@app.callback(
    Output("modal", "className"),
    [Input("help-icon", "n_clicks"), 
     Input("close-modal", "n_clicks")],
    prevent_initial_call=True
)
def toggle_modal(open_clicks, close_clicks):
    ctx = dash.callback_context.triggered[0]['prop_id']
    if ctx == "help-icon.n_clicks":
        return "modal show"
    return "modal"

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=8050, debug=True)
