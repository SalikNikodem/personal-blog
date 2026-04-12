from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Article {self.title}>'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    articles = Article.query.order_by(Article.date).all()
    return render_template('admin.html', articles=articles)

@app.route('/admin/add', methods=['POST', 'GET'])
def add():
    return render_template('new_article.html', mode='add')

if __name__ == '__main__':
    app.run(debug=True)

