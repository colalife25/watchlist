from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from sqlalchemy import select

from watchlist.models import User, Movie
from watchlist.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': # 判断是否是POST请求
        if not current_user.is_authenticated:
            return redirect(url_for('main.index'))
        
        title = request.form.get('title').strip() # 传入表单对应输入字段的 name 值
        year = request.form.get('year').strip()
        
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('main.index')) # 重定向回主页
       
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('main.index'))
        
    movies = db.session.execute(select(Movie)).scalars().all() # 读取所有电影记录
    return render_template('index.html', movies=movies)

@main_bp.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = db.get_or_404(Movie, movie_id)

    if request.method == 'POST': # 判断是否是POST请求
        
        title = request.form.get('title').strip() # 传入表单对应输入字段的 name 值
        year = request.form.get('year').strip()
        
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('main.edit', movie_id=movie_id)) # 重定向回主页
        
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('main.index'))
    
    return render_template('edit.html', movie=movie) # 传入被编辑的电影记录

@main_bp.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('main.index'))

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('main.settings'))
        
        user = db.session.get(User, current_user.id)
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('main.index'))
    
    return render_template('settings.html')
