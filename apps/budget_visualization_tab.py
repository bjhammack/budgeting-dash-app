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
def get_data(user, password):
    data = dc.Data(user=user, password=password)
    today = date.today()
    invoice_df = data.display_invoices()
    invoice_df.loc[:,'date'] = pd.to_datetime(invoice_df.loc[:, 'date']).dt.strftime('%m/%d/%Y')
    categories = [{'label':i,'value':i} for i in invoice_df.loc[:,'category'].sort_values().unique()]
    expense_df = data.display_invoices(invoice_type='Expense')
    expense_summary = data.annual_summary()
    income_summary = data.annual_summary(invoice_type='Income')
    net_income = data.net_income()
    balances = data.display_balances().round(2)
    balance_names = [{'label':i,'value':i} for i in balances.loc[:,'name'].sort_values().unique()]
    expense_graph_df = expense_df.loc[:,['date','value']]
    expense_graph_df.loc[:,'Year-Month'] = pd.DatetimeIndex(expense_graph_df.loc[:, ('date')]).year.astype(str) \
                                    +'_'+ pd.DatetimeIndex(expense_graph_df.loc[:, ('date')]).month.astype(str)
    expense_graph_df = expense_graph_df.loc[:,['Year-Month','value']].groupby(by=['Year-Month']).sum().sort_values(by='Year-Month')
    expense_fig = px.line(expense_graph_df.loc[:].rename(columns={'value':'Expenses'}).reset_index(), x='Year-Month',y='Expenses')
    
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

data = get_data('.',None)

layout = html.Div([
            html.Div([
                html.H4(children='Expense Graph'),
                dcc.Graph(id='expense-figure',figure=data['expense_fig'])
            ])
        ], className='summary-grid')