from datetime import datetime
import time
from flask import render_template, session, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db


from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, PostCase, InputGene, ManageCase, CreatSuper

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
    return render_template('login.html', title="Sign In", form=form)

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
        flash('Your changes have been saved.')
        #current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET': #填入旧的值
        #form.username.data = current_user.username
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

#username = db.Column(db.String(64), index=True, unique=True)
#email = db.Column(db.String(120), index=True, unique=True)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    username=current_user.username
    form=CreatSuper()
    if username == "admin":
        if form.validate_on_submit():
            # 判断超级用户在不在当前的列表里面，如果不在直接返回
            # 否则添加进去
            superuser1 = User.query.filter_by(username=form.supername.data).first()
            superuser2 = Superuser.query.filter_by(username=form.supername.data).first()
            if superuser1:
                if superuser2:
                    return render_template('error.html', msg="Super user is already existence")
                else:
                    tempspueruser = Superuser(username = superuser1.username, email = superuser1.email,
                    last_seen=superuser1.last_seen)
                    db.session.add(tempspueruser)
                    db.session.commit()
                    flash('You submit is Success!')
                    return render_template('creat_spuer.html', title="admin", form=form, admin=True)
            else:
                return render_template('error.html', msg="Is not an existing username")
        return render_template('creat_spuer.html', title="admin", form=form, admin=True)
    else:
        return render_template('creat_spuer.html', title="admin", form=form)

@app.route('/inputgene', methods=['GET', 'POST'])
@login_required
def inputgene():
    form = InputGene()
    case = Case.query.all()
    superuser = Superuser.query.filter_by(username=current_user.username).first()
    if not case:
        if superuser:
            return render_template('input.html', title="input", no_case=True, super_user=True)
        else:
            return render_template('input.html', title="input")
    if form.validate_on_submit():
        return render_template('input.html', title="input", case=case, show_case=True)

    return render_template('input.html', title="input", form=form, case=case, show_case=True)
    # return render_template('about.html')

# @app.route('/<username>/inputgene/<casename>', methods=['GET', 'POST'])
@app.route('/inputgene/<casename>', methods=['GET', 'POST'])
@login_required
def inputgene_case(casename):
    #找到当前的case基于casename
    case = Case.query.filter_by(casename=casename).first()
    form = InputGene()
    # return render_template('error.html', msg="qingchongxintianxie")
    if form.validate_on_submit():
        if len(form.inputgene.data.split( )) == 2:
            
            title = form.inputgene.data.split( )[0]
            body = form.inputgene.data.split( )[1]

            context = title + ' ' + body
            exchange = Exchange(exchange_record = context,timestamp = datetime.utcnow(),
                username= current_user.username, case_id = case.id)
            db.session.add(exchange)
            db.session.commit()

            if Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).all():
                if Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).all():
                    temp1 = Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).first().self_body
                    temp2 = Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).first().self_body

                    temp_title = temp1 + ' ' + body + ' ' + temp2
                    temp_title = ' '.join(list(set(temp_title.split())))
                    Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).first().self_body = temp_title

                    temp_body = temp2 + ' ' + title + ' ' + temp1
                    temp_body = ' '.join(list(set(temp_body.split())))
                    Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).first().self_body = temp_body
                    db.session.commit()
                else:
                    temp1 =Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).first().self_body 

                    temp_title = temp1 + ' ' + body
                    temp_title = ' '.join(list(set(temp_title.split())))
                    Persongene.query.filter(and_(Persongene.self_gene == title, Persongene.case_id == case.id)).first().self_body = temp_title

                    temp_body = title + ' ' + temp1
                    temp_body = ' '.join(list(set(temp_body.split())))
                    persongene = Persongene(self_gene = body, self_body = temp_body, case_id=case.id, username=current_user.username)

                    db.session.add(persongene)
                    db.session.commit()
            else:
                if Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).all(): 
                    temp2 = Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).first().self_body

                    temp_title = body + ' ' + temp2
                    temp_title = ' '.join(list(set(temp_title.split())))
                    persongene = Persongene(self_gene = title, self_body = temp_title, case_id=case.id, username=current_user.username)
                    
                    temp_body =  temp2 + ' ' + title
                    temp_body = ' '.join(list(set(temp_body.split())))
                    Persongene.query.filter(and_(Persongene.self_gene == body, Persongene.case_id == case.id)).first().self_body = temp_body
                    
                    db.session.add(persongene)
                    db.session.commit()
                else:
                    persongene1 = Persongene(self_gene = title, self_body = body, case_id = case.id, username = current_user.username)
                    persongene2 = Persongene(self_gene = body, self_body = title, case_id = case.id, username = current_user.username)
                    db.session.add(persongene1)
                    db.session.add(persongene2)
                    db.session.commit()
            flash('You submit is success! you submit is [{}]'.format(title + " " + body))
            # return str(form.inputgene.data)
            # return render_template('error.html', msg=title+body)
        else:
            flash('You submit is error!')
            return render_template('error.html', msg="Right submit is such as '1 2'")

#整体处理完成之后还需要把这次提交放到交换记录里面
    return render_template('input.html', title="input", form=form,
    case=case, casename1=casename)
    # return render_template('about.html')

@app.route('/showresult/<casename>', methods=['GET', 'POST'])
@login_required
def show_result(casename):
    result = []
    case = Case.query.filter_by(casename=casename).first()
    resultp = Persongene.query.filter(Persongene.case_id == case.id).all()
    for iresult in resultp:
        if case.infect_id in iresult.self_body:
            result.append([iresult.self_gene, "OK"])
        else:
            result.append([iresult.self_gene, "ERR"])
    return render_template('showresult.html', title="showresult",
        result=result, show_result=case.is_show_result, show_source=case.is_show_source, 
        case=case, casename=casename)

@app.route('/showrecord/<casename>', methods=['GET', 'POST'])
@login_required
def show_record(casename):
    case = Case.query.filter_by(casename=casename).first()
    record = Exchange.query.filter(Exchange.case_id == case.id).all()
    return render_template('showrecord.html', title="showrecord", 
       record=record, show_record=case.is_show_record, case=case, casename=casename)

#管理特定的case
#@csrf.exempt
@app.route('/manage/<casename>', methods=['GET', 'POST'])
@login_required
def manage_case(casename):
    superuser = Superuser.query.filter_by(username=current_user.username).first()
    curr_case = Case.query.filter_by(casename=casename).first()
    case = Case.query.filter(and_(Case.casename == casename, Case.Superuser_id == superuser.id)).first()
    if not case:
        return render_template('error.html', title="Error", msg="You are not this case owner")

    form = ManageCase()
    if form.validate_on_submit():
        if form.infect_id.data:
            curr_case.infect_id = form.infect_id.data
        curr_case.is_show_result = form.show_result.data
        curr_case.is_show_record = form.show_record.data
        curr_case.is_show_source = form.show_source.data
        curr_case.allow_post = form.allow_post.data
        db.session.commit()
        flash('Your changes have been saved.')
    
    #无论如何和都需要填入旧的值
    form.infect_id.data = curr_case.infect_id
    form.show_result.data = curr_case.is_show_result
    form.show_record.data = curr_case.is_show_record
    form.show_source.data = curr_case.is_show_source
    form.allow_post.data = curr_case.allow_post

    result = []
    resultp = Persongene.query.filter(Persongene.case_id == curr_case.id).all()
    for iresult in resultp:
        if not case.infect_id:
            result.append([iresult.self_gene, "OK"])
        elif case.infect_id in iresult.self_body or case.infect_id in iresult.self_gene:
            result.append([iresult.self_gene, "Infecting"])
        else:
            result.append([iresult.self_gene, "OK"])
    record = Exchange.query.filter(Exchange.case_id == curr_case.id).all()
    return render_template('manage.html', title='Edit Profile', form=form,
        case=curr_case, result=result, record=record)

#显示所有case
@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    #是否是超级用户如果不是，直接提示错误
    if not current_user.username:
        return "123"
    superuser = Superuser.query.filter_by(username=current_user.username).first()
    if not superuser:
        return render_template('error.html', title="Error", msg="You are not a teacher")
    form = PostCase()
    #显示当前用户所创建的所有case，并且提供一个创建新case的按钮
    return render_template('manage_case.html', title="Manage", form=form,
        show_case=True,username=current_user.username, case=superuser.cases)

@app.route('/<username>/creat', methods=['GET', 'POST'])
@login_required
def creat(username):
    #是否是超级用户如果不是，直接提示错误
    superuser = Superuser.query.filter_by(username=username).first()
    if not superuser:
        return render_template('error.html', title="Error", msg="You are not a teacher")
    
    form = PostCase()
    if form.validate_on_submit():
        if Case.query.filter_by(casename=form.casename.data).first():
            flash('Case is existence!')
            return render_template('creat.html', title="CreatCase", form=form)
        else:
            case = Case(casename = form.casename.data,
            infect_id = form.infect_id.data, 
            is_show_result = form.show_result.data,
            is_show_record = form.show_record.data,
            is_show_source = form.show_source.data,
            allow_post = form.allow_post.data,
            Superuser_id = superuser.id)
            db.session.add(case)
            db.session.commit()
            return redirect(url_for('manage_case', casename=form.casename.data))
    #开始处理数据写入数据库
    return render_template('creat.html', title="CreatCase", form=form)