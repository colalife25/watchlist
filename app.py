import os
import sys
import click
from pathlib import Path

from flask import Flask, url_for, render_template, redirect, flash, request
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

SQLITE_PREFIX = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_PREFIX + str(Path(app.root_path) / 'data.db')
app.config['SECRET_KEY'] = 'dev'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

class Movie(db.Model):
    __tablename__ = 'movie'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60))
    year: Mapped[str] = mapped_column(String(4))

@app.cli.command()
def forge():
    """Generate fake data."""
    db.drop_all()
    db.create_all()

    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1998'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1999'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    
    db.session.commit()
    click.echo('Done.')

@app.cli.command('init-db')
@click.option('--drop', is_flag=True, help='Create after drop.')
def init_database(drop):
    """Initialize the database."""
    if drop: # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') # 输出提示信息

@app.context_processor
def inject_user():
    user = db.session.execute(select(User)).scalar()
    return dict(user=user)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': # 判断是否是POST请求
        # 获取表单数据
        title = request.form.get('title').strip() # 传入表单对应输入字段的 name 值
        year = request.form.get('year').strip()
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
        

    movies = db.session.execute(select(Movie)).scalars().all() # 读取所有电影记录
    return render_template('index.html', movies=movies)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = db.get_or_404(Movie, movie_id)

    if request.method == 'POST': # 判断是否是POST请求
        # 获取表单数据
        title = request.form.get('title').strip() # 传入表单对应输入字段的 name 值
        year = request.form.get('year').strip()
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('edit', movie_id=movie_id)) # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    
    return render_template('edit.html', movie=movie) # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))