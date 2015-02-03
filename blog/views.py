from blog import app, db, lm
from blog.models import User, Project, Blogpost
from blog.forms import LoginForm, BlogpostForm
from flask import Flask, render_template, request, flash, session, redirect, url_for, Markup
from flask.ext.login import login_user, logout_user, current_user, login_required
import json
import markdown
import html2text

@app.route('/')
def hello_world():
	blogposts = Blogpost.query.order_by(Blogpost.id.desc()).limit(5).all()
	projects = Project.query.all()
	for blog in blogposts[:]:
		if blog is not None and not blog.is_deleted():
			blog.blog_content = Markup(markdown.markdown(blog.blog_content))
		else:
			blogposts.remove(blog)
	if current_user.is_authenticated():
		return render_template("blocks_main.html", blogposts=blogposts, projects=projects, admin=True)
	return render_template("blocks_main.html", blogposts=blogposts, projects=projects)

@app.route("/submit_blogpost", methods=['POST'])
@login_required
def submit_blog():
	form = BlogpostForm()
	blogpost = Blogpost(
		name=current_user.username,
		blog_content=form.blog_content.data,
		title=form.title.data,
		url_title=form.url_title.data
		)
	db.session.add(blogpost)
	db.session.commit()
	return redirect("/"+form.url_title.data)


@app.route('/create_blogpost/', methods=['GET','POST'])
@login_required
def new_blogpost():
	form = BlogpostForm()
	if request.method == "POST":
		return render_template("ajax_create_blogpost.html", form=form)
	return render_template("blocks_create_blogpost.html", form=form)

@app.route('/edit_blogpost', methods=['POST'])
@login_required
def edit_blogpost_commit():
	form = BlogpostForm()
	blogpost = Blogpost.query.filter_by(url_title=form.url_title.data).first()
	blogpost.blog_content = form.blog_content.data
	blogpost.title = form.title.data
	blogpost.url_title = form.url_title.data
	db.session.commit()
	return redirect("/"+blogpost.url_title)

@app.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash(u'Successfully logged in as %s' % form.user.username)
		session['user_id'] = form.user.id
		form = BlogpostForm()
		return render_template("ajax_create_blogpost.html", form=form)
	if request.method == 'POST':
		return "false"
	return render_template("blocks_login.html", form=form)


@app.route('/projects')
def projects():
	return render_template("projects.html")


@app.route('/<value>/')
def check_for_blogpost(value):
	blogpost = Blogpost.query.filter_by(url_title=value).first_or_404()
	blogpost.blog_content = Markup(markdown.markdown(blogpost.blog_content))
	if current_user.is_authenticated():
		return render_template("blocks_blogpost.html", blog=blogpost, admin=True)
	return render_template("blocks_blogpost.html", blog=blogpost)

@app.route('/<value>/edit')
@login_required
def edit_blogpost(value):
	blogpost = Blogpost.query.filter_by(url_title=value).first_or_404()
	form = BlogpostForm()
	h = html2text.HTML2Text()
	form.blog_content.data = h.handle(Markup(markdown.markdown(blogpost.blog_content)))
	form.title.data = h.handle(Markup(markdown.markdown(blogpost.title)))
	form.url_title.data = h.handle(Markup(markdown.markdown(blogpost.url_title)))
	return render_template("blocks_edit_blogpost.html", form=form)

@app.route('/<value>/delete')
@login_required
def delete_blogpost(value):
	blogpost = Blogpost.query.filter_by(url_title=value).first_or_404()
	blogpost.delete()
	db.session.commit()
	return redirect("/")

@app.route('/deleted_posts')
@login_required
def get_deleted():
	blogposts = Blogpost.query.filter_by(deleted=True).all()
	blog_url_titles = []
	for blog in blogposts:
		blog_url_titles.append(blog.url_title)
	return json.dumps(blog_url_titles)

@lm.user_loader
def load_user(userid):
	return User.query.get(int(userid))

@lm.unauthorized_handler
def unauthorized():
	return redirect("/login")