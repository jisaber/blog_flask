from app import appvar

@appvar.route('/')
@appvar.route('/index')
def index():
    user = {'username': 'zhuxiang'}
    return '''
    <html>
        <head>
            <title>Z</title>
        </head>
        <body>
            <h1>Hello, ''' + user['username'] + '''!</h1>
        </body>
    </html>'''