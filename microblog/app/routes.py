from datetime import datetime
import time
from flask import render_template, session, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db


from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, PostCase, InputGene

#下面是进行DB操作的内容
from app.models import User, Post, Case, Exchange, Superuser, Persongene
from operator import and_, or_

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
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
    return render_template('creat.html', title="Sign In", form=form)

@app.route('/creat', methods=['GET', 'POST'])
def creat():
    form = PostCase()
    if form.validate_on_submit():
        return str(form.casename.data) + str(form.infect_id.data) +  str(form.show_result.data == False) + str(form.show_exchange.data) + str(form.show_source.data) + str(form.allow_post.data)

    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first()
    #     if user is None or not user.check_password(form.password.data):
    #         flash('Invalid username or password')
    #         return redirect(url_for('login'))
    #     login_user(user, remember=form.remember_me.data)
    #     next_page = request.args.get('next')
    #     if not next_page or url_parse(next_page).netloc != '':
    #         next_page = url_for('index')
    #     return redirect(next_page)
    return render_template('creat.html', title="Sign In", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
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

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/infectious')
@login_required
def infectious():
    return render_template('infectious.html')

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET': #填入旧的值
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/inputgene', methods=['GET', 'POST'])
def inputgene():
    form = InputGene()
    case = Case.query.all()
    if form.validate_on_submit():
        return str(form.inputgene.data)
    return render_template('input.html', title="input", form=form, case=case, show_case=True)
    # return render_template('about.html')

# @app.route('/<username>/inputgene/<casename>', methods=['GET', 'POST'])
@app.route('/inputgene/<casename>', methods=['GET', 'POST'])
def inputgene_case(casename):
    #找到当前的case基于casename
    case = Case.query.filter_by(casename=casename).first()
    form = InputGene()
    # return render_template('error.html', msg="qingchongxintianxie")
    if form.validate_on_submit():
        if len(form.inputgene.data.split( )) == 2:
            
            title = form.inputgene.data.split( )[0]
            body = form.inputgene.data.split( )[1]
            flash('You submit is success! you submit is [{}]'.format(title + " " + body))
            # return render_template('input.html', title="input", form=form)

            # user = User(username=form.username.data, email=form.email.data)
            # user.set_password(form.password.data)
            # db.session.add(user)
            # db.session.commit()

            if Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).all():
                if Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).all():
                    temp1 = Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).first().self_body
                    temp2 = Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).first().self_body

                    temp_title = temp1 + ' ' + body + ' ' + temp2 
                    Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).first().self_body = temp_title

                    temp_body = temp2 + ' ' + title + ' ' + temp1
                    Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).first().self_body = temp_body
                    db.session.commit()
                else:
                    temp1 =Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).first().self_body 

                    temp_title = temp1 + ' ' + body
                    Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).first().self_body = temp_title

                    temp_body = title + ' ' + temp1
                    persongene = Persongene(self_gene = body, self_body = temp_body, case_id=case.id, username=current_user.username)

                    db.session.add(persongene)
                    db.session.commit()
            else:
                if Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).all(): 
                    temp2 = Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).first().self_body

                    temp_title = body + ' ' + temp2

                    persongene = Persongene(self_gene = title, self_body = temp_title, case_id=case.id, username=current_user.username)
                    
                    temp_body =  temp2 + ' ' + title
                    Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).first().self_body = temp_body
                    
                    db.session.add(persongene)
                    db.session.commit()
                else:
                    persongene1 = Persongene(self_gene = title, self_body = body, case_id = case.id, username = current_user.username)
                    persongene2 = Persongene(self_gene = body, self_body = title, case_id = case.id)
                    db.session.add(persongene1)
                    db.session.add(persongene2)
                    db.session.commit()
            # return str(form.inputgene.data)
            # return render_template('error.html', msg=title+body)
        else:
            flash('You submit is error!')
            return render_template('error.html', msg="123")

#整体处理完成之后还需要把这次提交放到交换记录里面
    return render_template('input.html', title="input", form=form)
    # return render_template('about.html')