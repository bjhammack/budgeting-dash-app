import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import home, budget_ben, budget_maddy, side_menu, top_menu
    
try:
    app.layout = html.Div([
        top_menu.layout,
        side_menu.layout,
        html.Div(id='page-content', className='content-div'),
        dcc.Location(id='url', refresh=False)
        ], className='page-div')
except:
    app.layout = html.Div(['404'])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/home':
        return home.layout
    elif pathname == '/apps/budgets/ben':
        return budget_ben.layout
    elif pathname == '/apps/budgets/maddy':
        return budget_maddy.layout
    else:
        return f'404 {pathname} not found.'

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
