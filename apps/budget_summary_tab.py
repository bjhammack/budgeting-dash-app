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

layout = html.Div([
                html.Div([
                    html.H4(children='Expense Summary'),
                    dash_table.DataTable(
                        id='expense-summary-table'
                        ,columns=[{'name':i,'id':i} for i in data['expense_summary'].columns]
                        ,data=data['expense_summary'].loc[:].to_dict('records')
                        ,style_as_list_view=True
                        ,style_cell={'font-family': "Lato",'font-size':'15px'}
                        )
                ]),

                html.Div([
                    html.H4(children='Net Income'),
                    dash_table.DataTable(
                        id='net-income-table'
                        ,columns=[{'name':i,'id':i} for i in data['net_income'].columns]
                        ,data=data['net_income'].loc[:].to_dict('records')
                        ,style_as_list_view=True
                        ,style_cell={'font-family': "Lato",'font-size':'15px'}
                        )
                ]),

                html.Div([
                    html.H4(children='Income Summary'),
                    dash_table.DataTable(
                        id='income-summary-table'
                        ,columns=[{'name':i,'id':i} for i in data['income_summary'].columns]
                        ,data=data['income_summary'].loc[:].to_dict('records')
                        ,style_as_list_view=True
                        ,style_cell={'font-family': "Lato",'font-size':'15px'}
                        )
                ]),

                html.Div([
                    html.H4(children='Balances'),
                    dash_table.DataTable(
                        id='balance-table'
                        ,columns=[{'name':i,'id':i} for i in data['balances'].loc[:,['Name','Funds']].columns]
                        ,data=data['balances'].loc[:].to_dict('records')
                        ,style_as_list_view=True
                        ,style_cell={'font-family': "Lato",'font-size':'15px'}
                        )
                ]),
            ], className='summary-grid')