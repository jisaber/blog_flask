## 运行方式
```
cd ./blog_flask/microblog
flask run --host 192.168.3.14 --port 6002
(http://192.168.3.14:6002/)
```
或者
```
cd ./blog_flask/microblog
flask run
(http://127.0.0.1:5000/)
```
## 项目用到的包
包名 安装方式 功能<br>
***
* python3.5.3  
(Python 3.5.3 (default, Sep 27 2018,   17:25:39)  
[GCC 6.3.0 20170516] on linux  
Type "help", "copyright", "credits" or   "license" for more information.) 

* flask-1.1.1<br>pip3 install flask

* python-dotenv-0.10.3<br>pip3 install python-dotenv 用来管理环境变量的

* flask-wtf<br>pip3 install flask-wtf 用来管理密码的校验值 Successfully installed WTForms-2.2.1 flask-wtf-0.14.2

* flask-sqlalchemy<br>管理数据库 pip3 install flask-sqlalchemy
Successfully installed SQLAlchemy-1.3.12 flask-sqlalchemy-2.4.1

* flask-migrate<br>数据库迁移工具pip3 install flask-migrat, Successfully installed Flask-Migrate-2.5.2 Mako-1.1.0 alembic-1.3.2 python-dateutil-2.8.1 python-editor-1.0.4 six-1.13.0
需要换个源pip3 install Flask-Migrate -i https://pypi.douban.com/simple

* flask-login<br>登录管理工具pip3 install flask-login, Successfully installed flask-login-0.4.1
