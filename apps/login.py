from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from app import app
from data_controller import Data

data = Data()
users = data.users

layout = html.Div([
			dcc.Input(id='login-username', type='text', placeholder='Username', style={'height':'50%'}),
			dcc.Input(id='login-password', type='password', placeholder='Password', style={'height':'50%'}),
			html.Button('Login', id='login-button', className='login-button', style={'height':'50%'}),
			html.Div(id='hidden-redirect-div',style={'display':'none'})
], className='login-div')

@app.callback(
    Output('username-store','data'),
    Output('hidden-redirect-div','children'),
    Input('login-button','n_clicks'),
    State('login-username','value'),
    State('login-password','value')
    )
def check_login(n_clicks, username, password):
	if n_clicks:
	    user_pass_pairs = users.loc[users.username.eq(username) & users.password.eq(password)]
	    if len(user_pass_pairs) > 0:
	    	return {'name':username, 'password':password}, dcc.Location(pathname='/apps/home',id='home-redirect')
	    else:
	    	return '', 'Incorrect Credentials'
	else:
		raise PreventUpdate
