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

sys.path.append('..')
import data_controller as dc

pd.options.mode.chained_assignment = None

data_funcs = dc.Data('.')

def get_data(user):
    data = dc.Data(user=user)
    today = date.today()
    invoice_df = data.display_invoices()
    invoice_df.loc[:,'Date'] = pd.to_datetime(invoice_df.loc[:, 'Date']).dt.strftime('%m/%d/%Y')
    categories = [{'label':i,'value':i} for i in invoice_df.loc[:,'Category'].sort_values().unique()]
    expense_df = data.display_invoices(invoice_type='Expense')
    expense_summary = data.annual_summary()
    income_summary = data.annual_summary(invoice_type='Income')
    net_income = data.net_income()
    balances = data.display_balances().round(2)
    balance_names = [{'label':i,'value':i} for i in balances.loc[:,'Name'].sort_values().unique()]
    expense_graph_df = expense_df.loc[:,['Date','Value']]
    expense_graph_df.loc[:,'Year-Month'] = pd.DatetimeIndex(expense_graph_df.loc[:, ('Date')]).year.astype(str) \
                                    +'_'+ pd.DatetimeIndex(expense_graph_df.loc[:, ('Date')]).month.astype(str)
    expense_graph_df = expense_graph_df.loc[:,['Year-Month','Value']].groupby(by=['Year-Month']).sum().sort_values(by='Year-Month')
    expense_fig = px.line(expense_graph_df.loc[:].rename(columns={'Value':'Expenses'}).reset_index(), x='Year-Month',y='Expenses')
    return_dict = {
        'data':data,
        'today':today,
        'invoice_df':invoice_df,
        'categories':categories,
        'expense_df':expense_df.loc,
        'expense_summary':expense_summary,
        'income_summary':income_summary,
        'net_income':net_income,
        'balances':balances,
        'balance_names':balance_names,
        'expense_fig':expense_fig
        }

    return return_dict

data = get_data('.')

layout = dcc.Tabs([
        dcc.Tab(label='Summary Tab', children=[
            html.Div([
                html.Div([
                    html.H4(children='Expense Summary'),
                    dash_table.DataTable(
                        id='expense-summary-table'
                        ,columns=[{'name':i,'id':i} for i in data['expense_summary'].columns]
                        ,data=data['expense_summary'].loc[:].to_dict('records')
                        )
                ]),

                html.Div([
                    html.H4(children='Net Income'),
                    dash_table.DataTable(
                        id='net-income-table'
                        ,columns=[{'name':i,'id':i} for i in data['net_income'].columns]
                        ,data=data['net_income'].loc[:].to_dict('records')
                        )
                ]),

                html.Div([
                    html.H4(children='Income Summary'),
                    dash_table.DataTable(
                        id='income-summary-table'
                        ,columns=[{'name':i,'id':i} for i in data['income_summary'].columns]
                        ,data=data['income_summary'].loc[:].to_dict('records')
                        )
                ]),

                html.Div([
                    html.H4(children='Balances'),
                    dash_table.DataTable(
                        id='balance-table'
                        ,columns=[{'name':i,'id':i} for i in data['balances'].columns]
                        ,data=data['balances'].loc[:].to_dict('records')
                        )
                ]),

                html.Div([
                    html.H4(children='Expense Graph'),
                    dcc.Graph(id='expense-figure',figure=data['expense_fig'])
                ])

            ], className='summary-grid')
        ]),

        dcc.Tab(label='Invoice Tab', children=[
            html.Div([

                html.Div([
                    html.H4(children='Invoices'),
                    dash_table.DataTable(
                        id='invoice-table',
                        columns=[{'name':i,'id':i} for i in data['invoice_df'].columns],

                        filter_action="native",
                        sort_action="native"
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
                        )]
                        , className='new-invoice-type'),
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
                        )]
                        , className='new-invoice-date'),
                    html.Button('New Invoice', id='submit-invoice', className='new-invoice-button', style={'height':'50%'})
                ], className='new-invoice-grid'),

                html.Div([
                    html.H4(children='Transfer Balance', className='new-invoice-head'),
                    html.Div([
                        dcc.Dropdown(
                            id='from-balance', style={'height':'50%','width':'176px','margin-left':'24px','position':'absolute'},
                            options=data['balance_names'],
                            placeholder='From'
                        )
                        ]),
                    html.Div([
                        dcc.Dropdown(
                            id='to-balance', style={'height':'25%','width':'176px','margin-left':'24px','position':'absolute'},
                            options=data['balance_names'],
                            placeholder='To'
                        )
                        ]),
                    html.Div([
                        dcc.Input(id='transfer-funds', type='number', placeholder='Funds', style={'height':'50%'})]),

                    html.Button('Transfer', id='transfer-balance', className='transfer-button', style={'height':'50%'})
                ], className='transfer-balance-grid'),

                html.Div([
                    html.H4(children='New Balance', className='new-invoice-head'),
                    html.Div([
                        dcc.Input(id='new-balance-name', type='text', placeholder='Name', style={'height':'50%'})]),
                    html.Div([
                        dcc.Input(id='new-balance-funds', type='number', placeholder='Funds', style={'height':'50%'})]),
                    html.Div([
                        dcc.Input(id='new-balance-goal', type='number', placeholder='Goal', style={'height':'50%'})]),
                    html.Div([
                         dcc.DatePickerSingle(
                            id='new-balance-goal-date',
                            clearable=True,
                            with_portal=True,
                            placeholder='Goal Date'
                            )]),

                    html.Button('New Balance', id='new-balance', className='balance-button', style={'height':'50%'})
                ], className='new-balance-grid')

            ], className='invoice-grid'),
            html.Div(id='hidden-div-invoice',style={'display':'none','visibility':'hidden'}),
            html.Div(id='hidden-div-transfer',style={'display':'none','visibility':'hidden'}),
            html.Div(id='hidden-div-balance',style={'display':'none','visibility':'hidden'}),
            html.Div(id='hidden-username-budget', style={'display':'none'}, children='')
        ])
    ])

@app.callback(
    Output('input-category','value'),
    [Input('category-dropdown','value')]
    )
def update_category(value):
    return value

@app.callback(
    Output('hidden-div-invoice','children'),
    [Input('submit-invoice', 'n_clicks')],
    [State('input-value', 'value')],
    [State('input-name', 'value')],
    [State('input-category', 'value')],
    [State('input-type', 'value')],
    [State('input-balance', 'value')],
    [State('input-date', 'date')],
    [State('username-store', 'data')]
    )
def new_invoice(n_clicks,value,name,category,invoice_type,balance,date,user_store):
    if n_clicks:
        input_dict = {'value':value,'name':name,'category':category,'invoice_type':invoice_type,'balance':balance,'date':date,'user':user_store['name']}
        data_funcs.new_invoice(input_dict)

@app.callback(
    Output('hidden-div-transfer','children'),
    [Input('transfer-balance', 'n_clicks')],
    [State('from-balance', 'value')],
    [State('to-balance', 'value')],
    [State('transfer-funds', 'value')],
    [State('username-store', 'data')]
    )
def transfer_balance(n_clicks,t_from,t_to,funds,user_store):
    if n_clicks:
        input_dict = {'value':funds,'name':f'From: {t_from}, To: {t_to}','category':'Transfers','invoice_type':'Transfer','balance':'','date':str(data['today']),'user':user_store['name']}
        data_funcs.new_invoice(input_dict)
        transfer_dict = {'from_balance':t_from,'to_balance':t_to,'funds':funds,'user':user_store['name']}
        data_funcs.transfer_balance(transfer_dict)

@app.callback(
    Output('hidden-div-balance','children'),
    [Input('new-balance', 'n_clicks')],
    [State('new-balance-name', 'value')],
    [State('new-balance-funds', 'value')],
    [State('new-balance-goal', 'value')],
    [State('new-balance-goal-date', 'date')],
    [State('username-store', 'data')]
    )
def new_balance(n_clicks,name,funds,goal,goal_date,user_store):
    if n_clicks:
        input_dict = {'name':name,'funds':funds,'goal':goal,'goal_date':goal_date,'user':user_store['name']}
        data_funcs.new_balance(input_dict)

@app.callback(
    Output('expense-summary-table','data'),
    Output('net-income-table','data'),
    Output('income-summary-table','data'),
    Output('balance-table','data'),
    Output('expense-figure','figure'),
    Output('invoice-table','data'),
    Output('category-dropdown','options'),
    Output('input-balance','options'),
    Output('input-date','date'),
    Output('from-balance','options'),
    Output('to-balance','options'),
    Input('new-balance','n_clicks'),
    Input('submit-invoice','n_clicks'),
    Input('transfer-balance','n_clicks'),
    Input('username-store','data')
    )
def update_data(clicks1,clicks2,clicks3,user):
    if user['name'] and user['name'] != '':
        data = get_data(user['name'])
        return data['expense_summary'].loc[:].to_dict('records'),data['net_income'].loc[:].to_dict('records')\
                ,data['income_summary'].loc[:].to_dict('records'),data['balances'].loc[:].to_dict('records')\
                ,data['expense_fig'],data['invoice_df'].loc[:].to_dict('records')\
                ,data['categories'],data['balance_names'],data['today'],data['balance_names'],data['balance_names']
    else:
        raise PreventUpdate