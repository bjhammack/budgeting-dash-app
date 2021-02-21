from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from app import app

layout = html.Div([
			html.Nav([
				html.Ul([
					html.Li([
						html.Div([
	 						html.I(id='logout-link',className='bi-box-arrow-in-right', style={'font-size':'30px','color':'white','float':'right','margin-right':'2%'}),
						], style={'width':'100%'})
					], className='topbar-li', style={'width':'100%'}),
				], className='topbar-ul', style={'width':'100%'})
			], className='topbar-nav', style={'width':'100%'}),
			html.Div(id="hidden-logout-div",style={'display':'none'})
		], className='topbar-div', style={'width':'100%'})

@app.callback(
	Output('username-store', 'clear_data'),
	Output('hidden-logout-div', 'children'),
	Input('logout-link','n_clicks')
	)
def logout(n_clicks):
	if n_clicks:
		return True, dcc.Location(pathname='/apps/login',id='login-redirect')
	else:
		raise PreventUpdate
