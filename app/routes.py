from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from .models import Todo, User
from . import db
from flask_wtf import FlaskForm  # ✨ Form dengan CSRF token otomatis
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

main = Blueprint('main', __name__)

# --- Form Definitions untuk CSRF dan Validasi ---
class TodoForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired(), Length(max=100)])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])

# --- Login Required Decorator ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Silakan login dulu.")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@main.route('/')
@login_required
def index():
    todos = Todo.query.all()
    form = TodoForm()
    return render_template('index.html', todos=todos or [], form=form)

@main.route('/add', methods=['POST'])
@login_required
def add():
    form = TodoForm()
    if form.validate_on_submit():
        task = form.task.data
        new_todo = Todo(task=task)
        db.session.add(new_todo)
        db.session.commit()
        current_app.logger.info(f"[ADD] User {session.get('user_id')} menambahkan task: {task}")
    else:
        flash('Task tidak boleh kosong dan maksimal 100 karakter.')
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
    form = TodoForm()
    if todo and form.validate_on_submit():
        todo.task = form.task.data
        db.session.commit()
    else:
        flash('Task update gagal. Pastikan isi task valid.')
    return redirect(url_for('main.index'))

# --- Register ---
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
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
    return render_template('register.html', form=form)

# --- Login ---
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            current_app.logger.info(f"[LOGIN] User {username} berhasil login.")
            flash('Login berhasil.')
            return redirect(url_for('main.index'))
        else:
            current_app.logger.warning(f"[LOGIN-FAILED] Percobaan login gagal untuk username: {username}")
            flash('Username atau password salah.')
    return render_template('login.html', form=form)

# --- Logout ---
@main.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('Anda telah logout.')
    return redirect(url_for('main.login'))
