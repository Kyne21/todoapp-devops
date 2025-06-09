from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from .models import Todo, User
from . import db

main = Blueprint('main', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Silakan login dulu.")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
@login_required
def index():
    todos = Todo.query.all()
    return render_template('index.html', todos=todos or [])

@main.route('/add', methods=['POST'])
@login_required
def add():
    task = request.form.get('task')
    if task:
        new_todo = Todo(task=task)
        db.session.add(new_todo)
        db.session.commit()
        current_app.logger.info(f"[ADD] User {session.get('user_id')} menambahkan task: {task}")
    return redirect(url_for('main.index'))

@main.route('/delete/<int:id>')
@login_required
def delete(id):
    todo = Todo.query.get(id)
    if todo:
        current_app.logger.info(f"[DELETE] User {session.get('user_id')} menghapus task: {todo.task}")
        db.session.delete(todo)
        db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/toggle/<int:id>')
@login_required
def toggle(id):
    todo = Todo.query.get(id)
    if todo:
        todo.done = not todo.done
        db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    todo = Todo.query.get(id)
    if todo:
        task = request.form.get('task')
        if task:
            todo.task = task
            db.session.commit()
    return redirect(url_for('main.index'))

# REGISTER
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username sudah terdaftar.')
                return redirect(url_for('main.register'))
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrasi berhasil, silakan login.')
            return redirect(url_for('main.login'))
        flash('Mohon isi username dan password.')
    return render_template('register.html')

# LOGIN
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            current_app.logger.info(f"[LOGIN] User {username} berhasil login.")
            flash('Login berhasil.')
            return redirect(url_for('main.index'))
        else:
            current_app.logger.warning(f"[LOGIN-FAILED] Percobaan login gagal untuk username: {username}")
            flash('Username atau password salah.')
    return render_template('login.html')


# LOGOUT
@main.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('Anda telah logout.')
    return redirect(url_for('main.login'))
