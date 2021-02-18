import dash

external_stylesheets = ['/style.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, requests_pathname_prefix='/apps/') # UNCOMMENT WHEN PUSHING
app.title = 'Budget'
app.config.suppress_callback_exceptions = True

server = app.server
