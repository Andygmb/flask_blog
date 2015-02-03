from blog.models import User
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators, TextAreaField, SubmitField

class LoginForm(Form):
	username = TextField('Username', [validators.Required()])
	password = PasswordField('Password', [validators.Required()])

	def validate(self):
		user = User.query.filter_by(username=self.username.data).first()
		if user is None:
			return False
		user.hash_password(self.password.data)
		if not user.verify_password(self.password.data):
			return False
		self.user = user
		return True

class BlogpostForm(Form):
	title = TextField("Title:")
	url_title = TextField("Short URL title:")
	blog_content = TextAreaField()
	submit = SubmitField()