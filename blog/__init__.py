from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.markdown import Markdown

app = Flask(__name__)
app.debug = True
app.secret_key = ""
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://andy:pw@localhost/blog'
lm = LoginManager()
lm.init_app(app)
db = SQLAlchemy(app)
Markdown(app)

from blog import views