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

from apps import budget_summary_tab, budget_invoice_tab, budget_projection_tab \
                ,budget_visualization_tab, budget_balance_tab

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
    
    expense_proj = data.projection_summary()

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
        'expense_fig':expense_fig,
        'proj_summary':expense_proj
        }

    return return_dict

data = get_data('.')

layout = dcc.Tabs([
        dcc.Tab(label='Summary', children=[
            budget_summary_tab.layout
        ]),
        dcc.Tab(label='Invoices', children=[
            budget_invoice_tab.layout
        ]),
        dcc.Tab(label='Balances', children=[
            budget_balance_tab.layout
        ]),
        dcc.Tab(label='Projections', children=[
            budget_projection_tab.layout
        ]),
        dcc.Tab(label='Visuals', children=[
            budget_visualization_tab.layout
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
    Output('expense-projection-table','data'),
    Input('new-balance','n_clicks'),
    Input('submit-invoice','n_clicks'),
    Input('transfer-balance','n_clicks'),
    Input('username-store','data')
    )
def update_data(clicks1,clicks2,clicks3,user):
    if user and user['name'] != '':
        data = get_data(user['name'])
        return data['expense_summary'].loc[:].to_dict('records'),data['net_income'].loc[:].to_dict('records')\
                ,data['income_summary'].loc[:].to_dict('records'),data['balances'].loc[:].to_dict('records')\
                ,data['expense_fig'],data['invoice_df'].loc[:].to_dict('records')\
                ,data['categories'],data['balance_names'],data['today'],data['balance_names'],data['balance_names']\
                ,data['proj_summary'].loc[:].to_dict('records')
    else:
        raise PreventUpdate