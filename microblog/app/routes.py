from flask import render_template, flash, redirect, url_for
from app import appvar
from app.forms import LoginForm

from flask_login import current_user, login_user
from app.models import User

from flask_login import login_required

@appvar.route('/')
@appvar.route('/index')
@login_required
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
    return render_template('index.html', title='Home Page', posts=posts)

from flask import request
from werkzeug.urls import url_parse
@appvar.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title="Sign In", form=form)

    
from flask_login import logout_user  
@appvar.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

from app import db
from app.forms import RegistrationForm

@appvar.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return "1111"
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)