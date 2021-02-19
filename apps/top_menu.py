from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from app import app

layout = html.Div([
			html.Nav([
				html.Ul([
					html.Li([
						html.Div([
							html.A([
	 							html.I(className='bi-globe2', style={'font-size':'30px','color':'white'}),
	 							],href='/apps/home/')
						])
					], className='topbar-li'),
				], className='topbar-ul')
			], className='topbar-nav')
		], className='topbar-div')