from flask import *
app = Flask(__name__)

blogposts = [
{
"title":"Title of a blog post that happens to be quite long indeed",
"short_title":"title",
"date":"01-01-1970",
"content":'words go here',
"color":'yellow',
"comments":[{"name":"Andy","comment":"Down with this sort of thing","date":"01-01-1970"},{"name":"Andy","comment":"Down with this sort of thing","date":"01-01-1970"}]
},
{
"title":"Title of a blog post that happens to be quite long indeed",
"short_title":"title",
"date":"01-01-1970",
"content":'words go here',
"color":'green'
}
]

@app.route('/')
def hello_world():
    return render_template("blocks_main.html", title="andygmb", blogposts=blogposts)


@app.route('/1')
def sup():
    return render_template("blocks_comments.html", title="andygmb", blogpost=blogposts[0])

if __name__ == '__main__':
	app.debug = True
	app.run()