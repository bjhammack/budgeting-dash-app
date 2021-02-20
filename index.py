import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import home, side_menu, top_menu, budget, login

try:
    app.layout = html.Div([
        top_menu.layout,
        side_menu.layout,
        html.Div(id='page-content', className='content-div'),
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='username-store', storage_type='session')
        ], className='page-div')
        
except:
    app.layout = html.Div(['404'])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              Input('username-store','data')
              )
def display_page(pathname, username_store):
    username_store = username_store or {'name':''}
    username = username_store['name']

    if pathname == '/apps/home' and username != '':
        return home.layout
    elif pathname == '/apps/budget' and username != '':
        return budget.layout
    elif username == '':
        return login.layout
    else:
        return f'404 {pathname} not found.'

if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
