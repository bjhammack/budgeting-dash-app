from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from app import app

layout = html.Div([
    dcc.Link('Budget', href='/apps/budget'),
    html.Br(),
    html.Br(),
    dcc.Link('Portfolio', href='/portfolio')
], className='home-navigation-div')
