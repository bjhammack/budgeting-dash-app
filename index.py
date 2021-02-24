import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app, server
from apps import home, side_menu, top_menu, budget, login

try:
    app.layout = html.Div([
        top_menu.layout,
        side_menu.layout,
        html.Div(id='page-content', className='content-div'),
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='username-store', storage_type='session')
        ], className='page-div', style={'position':'relative'})
        
except:
    app.layout = html.Div(['404'])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              Input('username-store','data')
              )
def display_page(pathname, username_store):
    username_store = username_store or {'name':'','password':''}
    username = username_store['name']
    password = username_store['password']
    if pathname == '/apps/home' and username != '' and password != '':
        return home.layout
    elif pathname == '/apps/budget' and username != '' and password != '':
        return budget.layout
    elif username == '' or password == '':
        return login.layout
    else:
        return f'404 {pathname} not found.'

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
