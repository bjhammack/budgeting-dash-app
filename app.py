import dash

external_stylesheets = ['/style.css','https://fonts.googleapis.com/icon?family=Material+Icons']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, requests_pathname_prefix='/apps/') # UNCOMMENT FINAL ARG WHEN LOADING ONTO APACHE SERVER
app.title = 'Dash Suite'
app.config.suppress_callback_exceptions = True

server = app.server
