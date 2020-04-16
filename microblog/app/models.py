from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

from app import db
from app import login

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    about_me = db.Column(db.String(4096))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(65535))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

#超级用户的内容，需要一个更加管理员的入口，可以新增何删除超级用户，这样我就可以随意给用户添加进来了
class Superuser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    cases = db.relationship('Case', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Superuser {}>'.format(self.username)

# 所有的测试，需要关联到某个超级id。
# 需要有超级ID才可以使用，每次读取之前都需要去超级ID中查看下
class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    casename = db.Column(db.String(64), index=True, unique=True)
    
    infect_id = db.Column(db.String(64))
    is_show_result = db.Column(db.Boolean)
    is_show_record = db.Column(db.Boolean)
    is_show_source = db.Column(db.Boolean)
    allow_post =  db.Column(db.Boolean)

    Superuser_id = db.Column(db.Integer, db.ForeignKey('superuser.id'))

    exchange_record = db.relationship('Exchange', backref='case_num', lazy='dynamic')
    person_gene = db.relationship('Persongene', backref='case_num', lazy='dynamic')

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #调试用的
    def __repr__(self):
        return '<Case {}>'.format(self.infect_id)

#传染过程的数据库，唯一链接到某个case, 仅作为展示用
class Exchange(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    exchange_record = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))

    def __repr__(self):
        return '<Exchange {}>'.format(self.id)

#真正的存储每个人的基因型的内容。username表示用户输入的内容
class Persongene(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    self_gene = db.Column(db.String(65535), index=True)
    self_body = db.Column(db.String(65535), index=True)

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))

    def __repr__(self):
        return '<Persongene {}>'.format(self.username)