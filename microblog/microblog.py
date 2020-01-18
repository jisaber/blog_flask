from app import appvar, db
from app.models import User, Post

@appvar.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}