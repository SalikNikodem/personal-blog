from functools import wraps
from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def check_auth(username, password):
    return username == 'admin' and password == 'admin123'

def authenticate():
    return Response(
        'Could not verify your access level.\n'
        'You have to login', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

class Article(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Article {self.title}>'
@app.route('/')
def index():
    articles = Article.query.order_by(Article.date).all()
    return render_template('index.html', articles=articles)

@app.route('/article/<int:id>')
def article(id):
    article = Article.query.get_or_404(id)
    return render_template('post.html', article=article)

@app.route('/admin')
@requires_auth
def admin():
    articles = Article.query.order_by(Article.id).all()
    return render_template('admin.html', articles=articles)

@app.route('/admin/add', methods=['POST', 'GET'])
@requires_auth
def add():
    if request.method == 'POST':
        article_title = request.form['title']
        article_content = request.form['content']
        date_str = request.form['date']
        article_date = datetime.strptime(date_str, '%Y-%m-%d')

        new_article = Article(title=article_title,
                              content=article_content,
                              date=article_date
                    )
        try:
            db.session.add(new_article)
            db.session.commit()
            return redirect('/admin')
        except:
            return 'There was an issue adding your article'

    return render_template('new_article.html', mode='add', article=None, today=datetime.utcnow().strftime('%Y-%m-%d'))


@app.route('/admin/edit/<int:id>', methods=['POST', 'GET'])
@requires_auth
def edit(id):
    article_to_edit = Article.query.get_or_404(id)

    if request.method == 'POST':
        article_to_edit.title = request.form['title']
        article_to_edit.content = request.form['content']
        date_str = request.form['date']
        article_to_edit.date = datetime.strptime(date_str, '%Y-%m-%d')

        try:
            db.session.commit()
            return redirect('/admin')
        except:
            return 'There was an issue editing your article'

    return render_template('new_article.html', mode='edit', article=article_to_edit)
@app.route('/admin/delete/<int:id>')
@requires_auth
def delete(id):
    article_to_delete = Article.query.get_or_404(id)

    try:
        db.session.delete(article_to_delete)
        db.session.commit()
        return redirect('/admin')
    except:
        return 'There was an issue deleting your article'

if __name__ == '__main__':
    app.run(debug=True)

