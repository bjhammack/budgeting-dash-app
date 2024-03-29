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
    today = date.today()
    invoice_df = data.display_invoices()
    invoice_df.loc[:,'date'] = pd.to_datetime(invoice_df.loc[:, 'date']).dt.strftime('%m/%d/%Y')
    categories = [{'label':i,'value':i} for i in invoice_df.loc[:,'category'].sort_values().unique()]
    balances = data.display_balances().round(2)
    balance_names = [{'label':i,'value':i} for i in balances.loc[:,'name'].sort_values().unique()]
    return_dict = {
        'today':today,
        'invoice_df':invoice_df,
        'categories':categories,
        'balance_names':balance_names,
        }

    return return_dict

data = get_data('.')

layout = html.Div([
            html.Div([
                html.H4(children='Invoices'),
                dash_table.DataTable(
                    id='invoice-table',
                    columns=[{'name':i,'id':i} for i in data['invoice_df'].columns],

                    filter_action="native",
                    sort_action="native"
                    ,style_as_list_view=False
                    ,style_cell={'font-family': "Lato",'font-size':'14px'}
                    )
            ], className='invoice-table-div'),
            html.Span(),

            html.Div([
                html.H4(children='New Invoice', className='new-invoice-head'),
                html.Div([
                    dcc.Input(id='input-value', type='number', placeholder='Value', style={'height':'50%'})]
                    , className='new-invoice-value'),
                html.Div([
                    dcc.Input(id='input-name', type='text', placeholder='Name', style={'height':'50%'})]
                    , className='new-invoice-name'),
                html.Div([
                    dcc.Input(id='input-category', type='text', placeholder='Category', style={'height':'25%'}),
                    dcc.Dropdown(
                        id='category-dropdown', style={'height':'25%','width':'176px','margin-left':'24px','position':'absolute'},
                        options=data['categories']
                    )
            ], className='new-invoice-category'),

                html.Div([
                    dcc.RadioItems(
                        id='input-type',
                        options=[
                            {'label': 'Income', 'value': 'Income'},
                            {'label': 'Expense', 'value': 'Expense'}
                        ],
                        value='Expense'
                    )
                ], className='new-invoice-type'),
                html.Div([
                    dcc.Dropdown(
                        id='input-balance', style={'height':'50%','width':'176px','margin-left':'24px','position':'absolute'},
                        options=data['balance_names'],
                        placeholder='Balance'
                    )
                ], className='new-invoice-balance'),
                html.Div([
                    dcc.DatePickerSingle(
                        id='input-date',
                        clearable=True,
                        with_portal=True,
                        date=data['today']
                    )
                ], className='new-invoice-date'),
                html.Button('New Invoice', id='submit-invoice', className='new-invoice-button', style={'height':'50%'})
            ], className='new-invoice-grid'),

            
            html.Div(id='hidden-div-invoice',style={'display':'none','visibility':'hidden'}),
            html.Div(id='hidden-div-transfer',style={'display':'none','visibility':'hidden'}),
            html.Div(id='hidden-div-balance',style={'display':'none','visibility':'hidden'}),
            html.Div(id='hidden-username-budget', style={'display':'none'}, children='')
        ], className='invoice-grid')

        