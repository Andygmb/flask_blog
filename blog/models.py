from blog import db
from datetime import date
from passlib.apps import custom_app_context as pwd_context
from flask.ext.login import UserMixin

class Blogpost(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	blog_content = db.Column(db.Text)
	name = db.Column(db.String(100))
	date = db.Column(db.Date)
	title = db.Column(db.String(140))
	url_title = db.Column(db.String(70), unique=True)
	deleted = db.Column(db.Boolean)

	def __init__(self, name, blog_content, title, url_title):
		self.name = name
		self.blog_content = blog_content
		self.date = date.today()
		self.title = title 
		self.url_title = url_title
		self.deleted = False

	def delete(self):
		self.deleted = True


class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140), unique=True)
	preview = db.Column(db.String(140))
	tldr = db.Column(db.Text)
	url = db.Column(db.String(140))
	deleted = db.Column(db.Boolean)

	def __init__(self, title, preview, tldr, url):
		self.title = title
		self.preview = preview
		self.tldr = tldr
		self.url = url

	def delete(self):
		self.deleted = True


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(40), unique=True)
	password = db.Column(db.String(150))

	def __init__(self, username, password):
		self.username = username
		self.password = self.hash_password(password)

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

	def __repr__(self):
		return '<User %r>' % (self.username)

db.create_all()