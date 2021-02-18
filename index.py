from importlib import reload
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import budget_ben, budget_maddy
    
app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/budgets/ben':
        return budget_ben.layout
    elif pathname == '/apps/budgets/maddy':
        return budget_maddy.layout
    else:
        return f'404 {pathname} not found.'

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
