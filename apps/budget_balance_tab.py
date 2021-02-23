from datetime import date
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import pandas as pd
from app import app
import plotly.express as px
import sys
import json

pd.options.mode.chained_assignment = None

sys.path.append('..')
import data_controller as dc

def get_data(user):
  data = dc.Data(user)
  balances = data.display_balances().round(2)
  balance_names = [{'label':i,'value':i} for i in balances.loc[:,'Name'].sort_values().unique()]
  return_dict = {
    'balances':balances,
    'balance_names':balance_names
  }

  return return_dict

data = get_data('.')
data_funcs = dc.Data('.')

def create_balance_div(index,name, funds, goal, goal_date):
  layout = html.Div([
          html.P(name, className='balance-p-name', id={'type':'balance-p-name','index':index}),
          dcc.Input(className='change-bname-input',value=name,id={'type':'change-bname-input','index':index},type='text',placeholder=name,style={'display':'none'}),
          html.I(className='bi-pencil-square', id={'type':'balance-edit-icon','index':index}),
          html.I(className='bi-check2-square', id={'type':'balance-submit-change-icon','index':index}, style={'display':'none'}),
          html.P(funds, className='balance-p-funds', id={'type':'balance-p-funds','index':index}),
          dcc.Input(className='change-bfunds-input',value=funds,id={'type':'change-bfunds-input','index':index},type='number',placeholder=funds,style={'display':'none'}),
          html.P(goal, className='balance-p-goal', id={'type':'balance-p-goal','index':index}),
          dcc.Input(className='change-bgoal-input',value=goal,id={'type':'change-bgoal-input','index':index},type='text',placeholder=goal,style={'display':'none'}),
          html.P(goal_date, className='balance-p-goal-date', id={'type':'balance-p-goal-date','index':index}),
          dcc.DatePickerSingle(className='change-bgoal-date-input',id={'type':'change-bgoal-date-input','index':index},clearable=True,with_portal=True,date=goal_date,style={'display':'none'})
          ], className='balance-div-child')
  return layout

data = get_data('.')

layout = html.Div([
            html.Div([], className='balance-div-parent',id='balance-div-parent'),
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
                html.H4(children='New Balance', className='new-balance-head'),
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
                        )
                ]),

                html.Button('New Balance', id='new-balance', className='balance-button', style={'height':'50%'})
            ], className='new-balance-grid')
        ], className='balance-grid')

@app.callback(
  Output('balance-div-parent', 'children'),
	Input('new-balance','n_clicks'),
  Input('submit-invoice','n_clicks'),
  Input('transfer-balance','n_clicks'),
  Input('username-store','data')
  )
def update_balances(clicks1,clicks2,clicks3,user):
    if user and user['name'] != '':
        data = get_data(user['name'])
        return [create_balance_div(k,i['Name'],i['Funds'],i['Goal'],i['Goal Date']) for k,i in enumerate(data['balances'].loc[:].to_dict('records'))]
    else:
        raise PreventUpdate

@app.callback(
  Output({'type':'change-bname-input','index':MATCH},'style'),
  Output({'type':'change-bfunds-input','index':MATCH},'style'),
  Output({'type':'change-bgoal-input','index':MATCH},'style'),
  Output({'type':'change-bgoal-date-input','index':MATCH},'style'),
  
  Output({'type':'balance-p-name','index':MATCH},'style'),
  Output({'type':'balance-p-funds','index':MATCH},'style'),
  Output({'type':'balance-p-goal','index':MATCH},'style'),
  Output({'type':'balance-p-goal-date','index':MATCH},'style'),
  
  Output({'type':'balance-edit-icon','index':MATCH},'style'),
  Output({'type':'balance-submit-change-icon','index':MATCH},'style'),

  Input({'type':'balance-edit-icon','index':MATCH},'n_clicks'),
  Input({'type':'balance-submit-change-icon','index':MATCH},'n_clicks'),

  State({'type':'balance-p-name','index':MATCH}, 'children'),
  State({'type':'balance-p-funds','index':MATCH}, 'children'),
  State({'type':'balance-p-goal','index':MATCH}, 'children'),
  State({'type':'balance-p-goal-date','index':MATCH}, 'children'),

  State({'type':'change-bname-input','index':MATCH}, 'value'),
  State({'type':'change-bfunds-input','index':MATCH}, 'value'),
  State({'type':'change-bgoal-input','index':MATCH}, 'value'),
  State({'type':'change-bgoal-date-input','index':MATCH}, 'date'),
  State('username-store', 'data')
  )
def edit_balance(edit_click,submit_click, cname, cfunds, cgoal, cgoal_date, name, funds, goal, goal_date, user):
  button_id = {'type':''}
  ctx = dash.callback_context
  if ctx.triggered:
    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])

  if button_id['type'] == 'balance-edit-icon':
    return {'display':''},{'display':''},{'display':''},{'display':''}\
          ,{'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'}\
          ,{'display':'none'},{'display':''}
  elif button_id['type'] == 'balance-submit-change-icon':
    if str(cname) != str(name) or str(cfunds) != str(funds) or str(cgoal) != str(goal) or str(cgoal_date) != str(goal_date):
      input_dict = {'cname':cname, 'cfunds':cfunds, 'cgoal':cgoal, 'cgoal_date':cgoal_date, 'name':name\
                    , 'funds':funds, 'goal':goal, 'goal_date':goal_date, 'user':user['name']}

      data_funcs.edit_balance(input_dict)

    return {'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'}\
          ,{'display':''},{'display':''},{'display':''},{'display':''}\
          ,{'display':''},{'display':'none'}
  else:
    raise PreventUpdate