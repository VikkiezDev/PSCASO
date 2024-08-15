import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
from astropy.coordinates import SkyCoord, Angle
import astropy.units as u

# Initialize the Dash app
def create_dash_app(flask_app):
    app = dash.Dash(server=flask_app, name="Dashboard", url_base_pathname="/edaizer/")
    
    # Define the layout
    app.layout = html.Div([
        html.H1("SDSS Data Explorer", style={'text-align': 'center', 'margin-top': '0'}),
        html.P("This application performs an intermediate level exploratory data analysis (EDA) on the SDSS dataset. You can explore different visualizations based on photometric data.", style={'text-align': 'center'}),
        
        # Centered Dropdown and Sky Map Below
        html.Div([
            html.Div([
                html.H3("Select Data Release", style={'text-align': 'center'}),
                dcc.Dropdown(
                    id='data-release-dropdown',
                    options=[
                        {'label': 'DR18', 'value': 'dr18'},
                        {'label': 'DR17', 'value': 'dr17'},
                        {'label': 'DR16', 'value': 'dr16'},
                        {'label': 'DR15', 'value': 'dr15'}
                    ],
                    value='dr18',
                    style={'width': '40%', 'margin': '0 auto', 'color': 'white'}
                ),
                html.Div(id='dataset-shape', style={'margin-top': '20px', 'text-align': 'center'})
            ], style={'width': '100%', 'text-align': 'center', 'margin-bottom': '20px'}),
            
            html.Div([
                dcc.Graph(id='sky-map')
            ], style={'width': '100%', 'margin-bottom': '20px'})
        ], style={'display': 'block'}),
        
        # Distributions
        html.Div([
            html.Div([
                dcc.Graph(id='class-distribution')
            ], style={'flex': '1'}),
            
            html.Div([
                dcc.Graph(id='dec-distribution')
            ], style={'flex': '1'}),
            
            html.Div([
                dcc.Graph(id='mjd-distribution')
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'margin-bottom': '20px'}),
        
        # Correlation Heatmaps
        html.Div([
            html.Div([
                dcc.Graph(id='star-correlation')
            ], style={'flex': '1'}),
            
            html.Div([
                dcc.Graph(id='galaxy-correlation')
            ], style={'flex': '1'}),
            
            html.Div([
                dcc.Graph(id='qso-correlation')
            ], style={'flex': '1'})
        ], style={'display': 'flex'})
    ], style={'background-color': '#0a0a0a', 'color': 'white'})

    # Callback to update dataset shape
    @app.callback(
        Output('dataset-shape', 'children'),
        Input('data-release-dropdown', 'value')
    )
    def update_dataset_shape(selected_dr):
        data = load_data(selected_dr)
        return f"Rows: {data.shape[0]}, Columns: {data.shape[1]}"

    # Callback to update sky map
    @app.callback(
        Output('sky-map', 'figure'),
        Input('data-release-dropdown', 'value')
    )
    def update_sky_map(selected_dr):
        data = load_data(selected_dr)
        
        galaxy = data[data['class'] == 'GALAXY']
        star = data[data['class'] == 'STAR']
        qso = data[data['class'] == 'QSO']
        
        fig = go.Figure()
        
        for df, name, color in [(galaxy, 'Galaxy', 'red'), (star, 'Star', 'blue'), (qso, 'Quasar', 'green')]:
            coords = SkyCoord(ra=df['ra'], dec=df['dec'], unit=(u.degree, u.degree))
            ra_rad = coords.ra.wrap_at(180 * u.deg).radian
            dec_rad = coords.dec.radian
            
            fig.add_trace(go.Scattergl(
                x=ra_rad,
                y=dec_rad,
                mode='markers',
                marker=dict(size=2, color=color, opacity=0.6),
                name=name
            ))
        
        fig.update_layout(
            title="Sky Map of Galaxies, Stars, and Quasars",
            xaxis_title="Right Ascension (radians)",
            yaxis_title="Declination (radians)",
            showlegend=True,
            height=600,
            template='plotly_dark'
        )
        
        return fig

    # Callback to update class distribution
    @app.callback(
        Output('class-distribution', 'figure'),
        Input('data-release-dropdown', 'value')
    )
    def update_class_distribution(selected_dr):
        data = load_data(selected_dr)
        class_counts = data['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        fig = px.pie(class_counts, values='count', names='class', title='Class Distribution')
        fig.update_layout(template='plotly_dark')
        return fig

    # Callback to update dec distribution
    @app.callback(
        Output('dec-distribution', 'figure'),
        Input('data-release-dropdown', 'value')
    )
    def update_dec_distribution(selected_dr):
        data = load_data(selected_dr)
        fig = px.box(data, x='class', y='dec', color='class', title='Dec Distribution by Class')
        fig.update_layout(template='plotly_dark')
        return fig

    # Callback to update MJD distribution
    @app.callback(
        Output('mjd-distribution', 'figure'),
        Input('data-release-dropdown', 'value')
    )
    def update_mjd_distribution(selected_dr):
        data = load_data(selected_dr)
        fig = go.Figure()
        for class_name in ['STAR', 'GALAXY', 'QSO']:
            class_data = data[data['class'] == class_name]
            fig.add_trace(go.Histogram(x=class_data['mjd'], name=class_name, opacity=0.7))
        fig.update_layout(title='Distribution of Modified Julian Date (MJD) by Class',
                        xaxis_title='Modified Julian Date (MJD)',
                        yaxis_title='Count',
                        barmode='overlay',
                        template='plotly_dark')
        return fig

    # Callbacks for correlation heatmaps
    @app.callback(
        [Output('star-correlation', 'figure'),
        Output('galaxy-correlation', 'figure'),
        Output('qso-correlation', 'figure')],
        Input('data-release-dropdown', 'value')
    )
    def update_correlation_heatmaps(selected_dr):
        data = load_data(selected_dr)
        
        figs = []
        for class_name in ['STAR', 'GALAXY', 'QSO']:
            class_data = data[data['class'] == class_name]
            corr = class_data[['u', 'g', 'r', 'i', 'z']].corr()
            fig = px.imshow(corr, 
                            labels=dict(x='Bands', y='Bands', color='Correlation'),
                            title=f'{class_name} Correlation',
                            color_continuous_scale='Reds',
                            template='plotly_dark')
            figs.append(fig)
        
        return figs

    return app

# Function to load data from a SQLite table
def load_data(table_name):
    conn = sqlite3.connect('data/data_release.db')
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load initial data
data = load_data('dr18')

# Convert MJD to datetime
_MJD_BASE_TIME_ = datetime.strptime('17/11/1858 00:00', '%d/%m/%Y %H:%M')
def convertMJD(x=0):
    return _MJD_BASE_TIME_ + timedelta(days=x)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
