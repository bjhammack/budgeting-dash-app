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
	 							html.I(className='bi-house', style={'font-size':'30px','color':'white'}),
	 							],href='/apps/home')
						])
					], className='sidebar-li'),
					html.Li([
						html.Div([
							html.A([
	 							html.I(className='bi-cash-stack', style={'font-size':'30px','color':'white'}),
	 							],href='/apps/budget')
						])
					], className='sidebar-li'),
					html.Li([
						html.Div([
							html.A([
	 							html.I(className='bi-bar-chart-line', style={'font-size':'30px','color':'white'}),
	 							],href='/apps/portfolio')
						])
					], className='sidebar-li'),
					html.Li([
						html.Div([
							html.A([
	 							html.I(className='bi-plus-square', style={'font-size':'30px','color':'white'}),
	 							],href='/apps/')
						])
					], className='sidebar-li')
				], className='sidebar-ul')
			], className='sidebar-nav2')
		], className='sidebar-div')

