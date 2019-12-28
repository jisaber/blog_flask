from flask import render_template, flash, redirect, url_for
from app import appvar
from app.forms import LoginForm

@appvar.route('/')
@appvar.route('/index')
def index():
    user = {'username': 'zhuxiang'}
    posts = [
        {
            'author':{'username':'Liuhuang', 'age':20,'heigh':185},
            'body':'welcome to zhejiang',
        },
        {
            'author':{'username':'Weizhang', 'age':25,'heigh':190},
            'body':"welcome to Hanghzou",
        },
    ]
    return render_template('index.html', user = user, posts = posts)

@appvar.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title="Sign In", form=form)