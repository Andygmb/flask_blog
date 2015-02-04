from blog import app, db, lm, cache
from blog.models import User, Project, Blogpost
from blog.forms import LoginForm, BlogpostForm, ProjectForm
from flask import Flask, render_template, request, flash, session, redirect, url_for, Markup
from flask.ext.login import login_user, logout_user, current_user, login_required
import json
import markdown
import html2text


@app.route('/')
@cache.cached(timeout=1)
def hello_world():
	title = "andygmb"
	blogposts = Blogpost.query.filter_by(deleted=False).order_by(Blogpost.id.desc()).limit(5).all()
	projects = Project.query.all()
	blogposts = markdown_parse(blogposts)
	if current_user.is_authenticated():
		return render_template("blocks_main.html", blogposts=blogposts, projects=projects, admin=True, title=title)
	return render_template("blocks_main.html", blogposts=blogposts, projects=projects, title=title)

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
	with app.app_context():
		cache.clear()
	return redirect("/"+form.url_title.data)


@app.route('/create_blogpost/', methods=['GET','POST'])
@login_required
def new_blogpost():
	title = "andygmb | create blogpost"
	form = BlogpostForm()
	if request.method == "POST":
		with app.app_context():
			cache.clear()
		return render_template("ajax_create_blogpost.html", form=form)
	return render_template("blocks_create_blogpost.html", form=form, title=title)

@app.route('/edit_blogpost', methods=['POST'])
@login_required
def edit_blogpost_commit():
	with app.app_context():
		cache.clear()
	form = BlogpostForm()
	blogpost = Blogpost.query.filter_by(url_title=form.url_title.data).first()
	blogpost.blog_content = form.blog_content.data
	blogpost.title = form.title.data
	blogpost.url_title = form.url_title.data
	db.session.commit()
	return redirect("/"+blogpost.url_title)


@app.route("/submit_project", methods=['POST'])
@login_required
def submit_project():
	form = ProjectForm()
	project = Project(
		title=form.title.data,
		preview=form.preview.data,
		url=form.url.data,
		tldr=form.tldr.data
		)
	db.session.add(project)
	db.session.commit()
	with app.app_context():
		cache.clear()
	return redirect("/projects")


@app.route('/create_project/', methods=['GET','POST'])
@login_required
def new_project():
	title = "andygmb | create project"
	form = ProjectForm()
	if request.method == "POST":
		with app.app_context():
			cache.clear()
		return render_template("ajax_create_project.html", form=form)
	return render_template("blocks_create_project.html", form=form, title=title)

@app.route('/edit_project', methods=['POST'])
@login_required
def edit_project_commit():
	with app.app_context():
		cache.clear()
	form = ProjectForm()
	project = Project.query.filter_by(title=form.title.data).first()
	project.title = form.title.data,
	project.preview = form.preview.data,
	project.url = form.url.data,
	project.tldr = form.tldr.data
	db.session.commit()
	return redirect("/projects")

@app.route('/<value>/edit_project')
@login_required
def edit_project(value):
	title = "andygmb | edit post"
	project = Project.query.filter_by(title=value).first_or_404()
	form = ProjectForm()
	h = html2text.HTML2Text()
	form.title.data = project.title
	form.preview.data = project.preview
	form.url.data = project.url 
	form.tldr.data = project.tldr
	return render_template("blocks_edit_project.html", form=form, title=title)

@app.route('/<value>/delete_project')
@login_required
def delete_project(value):
	with app.app_context():
		cache.clear()
	project = Project.query.filter_by(title=value).first_or_404()
	project.delete()
	db.session.commit()
	return redirect("/projects")

@app.route('/<value>/undelete_project')
@login_required
def undelete_project(value):
	with app.app_context():
		cache.clear()
	project = Project.query.filter_by(title=value).first_or_404()
	project.deleted = False
	db.session.commit()
	return redirect("/projects")

@app.route('/deleted_projects')
@login_required
def get_deleted_projects():
	title = "andygmb | deleted projects"
	project = Project.query.filter_by(deleted=True).all()
	return render_template("blocks_undelete_projects.html", projects=project, admin=True, title=title)


@app.route('/deleted_posts')
@login_required
def get_deleted():
	title = "andygmb | deleted posts"
	blogposts = Blogpost.query.order_by(Blogpost.id.desc()).filter_by(deleted=True).all()
	for blog in blogposts[:]:
		blog.blog_content = Markup(markdown.markdown(blog.blog_content))
	return render_template("blocks_undelete_blogs.html", blogposts=blogposts, admin=True, title=title)


@app.route('/login',methods=['GET','POST'])
def login():
	title = "andygmb | login"
	form = LoginForm()
	if form.validate_on_submit():
		session['user_id'] = form.user.id
		form = BlogpostForm()
		return render_template("ajax_create_blogpost.html", form=form)
	if request.method == 'POST':
		return "false"
	return render_template("blocks_login.html", form=form, title=title)


@app.route('/projects')
def projects():
	title = "andygmb | projects"
	projects = Project.query.order_by(Project.id.desc()).all()
	if request.is_xhr:
		return render_template("blocks_projects.html", ajax=True, projects=projects)
	return render_template("blocks_projects.html", ajax=False, projects=projects, title=title)

@app.route('/blog')
def blogs():
	title = "andygmb | blog"
	blogposts = Blogpost.query.order_by(Blogpost.id.desc()).limit(5).all()
	blogposts = markdown_parse(blogposts)
	if request.is_xhr:
		return render_template("blocks_blogposts.html", ajax=True, blogposts=blogposts)
	if current_user.is_authenticated():
		return render_template("blocks_blogposts.html", blogposts=blogposts, admin=True, title=title)
	return render_template("blocks_blogposts.html", ajax=False, blogposts=blogposts, title=title)

@app.route('/more/<b_id>')
@cache.memoize(timeout=600)
def get_more_from_id(b_id):
	title = "andygmb | older posts"
	maxlength = int(Blogpost.query.order_by(Blogpost.id.desc()).first().id)
	b_id = int(b_id)
	if b_id > maxlength:
		return redirect("/")

	blogposts = Blogpost.query\
				.filter(Blogpost.id.between(int(b_id)-5, b_id), Blogpost.deleted != True)\
				.order_by(Blogpost.id.desc()).limit(5).all()

	projects = Project.query.all()

	if len(blogposts):
		blogposts = markdown_parse(blogposts)
	if current_user.is_authenticated():
		return render_template("blocks_main.html", blogposts=blogposts, projects=projects, admin=True, prev=True, title=title)
	return render_template("blocks_main.html", blogposts=blogposts, projects=projects, prev=True, title=title)

@app.route('/prev/<b_id>')
@cache.memoize(timeout=600)
def get_prev_from_id(b_id):
	title = "andygmb | newer posts"
	prev = True
	maxlength = int(Blogpost.query.order_by(Blogpost.id.desc()).first().id)
	b_id = int(b_id)
	if b_id >= (maxlength - 5):
		prev = False

	blogposts = Blogpost.query\
				.filter(Blogpost.id.between(int(b_id), int(b_id)+5), Blogpost.deleted != True)\
				.order_by(Blogpost.id.desc()).limit(5).all()

	projects = Project.query.all()
	if len(blogposts) == 5:
		blogposts = markdown_parse(blogposts)
	elif len(blogposts) < 5:
		return redirect("/")
	if current_user.is_authenticated():
		return render_template("blocks_main.html", blogposts=blogposts, projects=projects, admin=True, prev=prev, title=title)
	return render_template("blocks_main.html", blogposts=blogposts, projects=projects, prev=prev, title=title)


@app.route('/<value>/')
@cache.memoize(timeout=600)
def check_for_blogpost(value):
	blogpost = Blogpost.query.filter_by(url_title=value).first_or_404()
	title = "andygmb | " + blogpost.title
	blogpost.blog_content = Markup(markdown.markdown(blogpost.blog_content))
	if current_user.is_authenticated():
		return render_template("blocks_blogpost.html", blog=blogpost, admin=True, title=title)
	if blogpost.deleted:
		return render_template("blocks_blog_deleted.html", blog=blogpost, title=title)
	return render_template("blocks_blogpost.html", blog=blogpost, title=title)

@app.route('/<value>/edit')
@login_required
def edit_blogpost(value):
	title = "andygmb | edit post"
	blogpost = Blogpost.query.filter_by(url_title=value).first_or_404()
	form = BlogpostForm()
	h = html2text.HTML2Text()
	form.blog_content.data = h.handle(Markup(markdown.markdown(blogpost.blog_content)))
	form.title.data = h.handle(Markup(markdown.markdown(blogpost.title)))
	form.url_title.data = h.handle(Markup(markdown.markdown(blogpost.url_title)))
	return render_template("blocks_edit_blogpost.html", form=form, title=title)

@app.route('/<value>/delete')
@login_required
def delete_blogpost(value):
	with app.app_context():
		cache.clear()
	blogpost = Blogpost.query.filter_by(url_title=value).first_or_404()
	blogpost.delete()
	db.session.commit()
	return redirect("/")

@app.route('/<value>/undelete')
@login_required
def undelete_blogpost(value):
	with app.app_context():
		cache.clear()
	blogpost = Blogpost.query.filter_by(url_title=value).first_or_404()
	blogpost.deleted = False
	db.session.commit()
	return redirect("/" + blogpost.url_title)

@lm.user_loader
def load_user(userid):
	return User.query.get(int(userid))

@lm.unauthorized_handler
def unauthorized():
	return redirect("/login")

def markdown_parse(blogposts):
	for blog in blogposts[:]:
		if blog is not None and not blog.deleted:
			blog.blog_content = Markup(markdown.markdown(blog.blog_content))
		else:
			blogposts.remove(blog)
	return blogposts
