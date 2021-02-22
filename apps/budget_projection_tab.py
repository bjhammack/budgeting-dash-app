from datetime import date
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import pandas as pd
from app import app
import plotly.express as px
import sys

pd.options.mode.chained_assignment = None

sys.path.append('..')
import data_controller as dc
def get_data(user):
    data = dc.Data(user=user)
    expense_proj = data.projection_summary()

    return_dict = {
        'proj_summary':expense_proj
        }

    return return_dict

data = get_data('.')

layout = html.Div([
                html.Div([
                    html.H4(children='Expense Projections'),
                    dash_table.DataTable(
                        id='expense-projection-table'
                        ,columns=[{'name':i,'id':i} for i in data['proj_summary'].columns]
                        ,data=data['proj_summary'].loc[:].to_dict('records')
                        ,style_as_list_view=False
                        ,style_cell={'font-family': "Lato",'font-size':'14px'}
                        )
                ])
            ], className='summary-grid')