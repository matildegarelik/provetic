from flask import render_template, redirect, url_for, request, flash, session
from app import app, db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        user = User(username=username, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso! Por favor inicia sesión.')
            return redirect(url_for('login'))
        except:
            flash('El nombre de usuario ya está en uso.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Inicio de sesión exitoso!')
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Por favor inicia sesión para acceder al dashboard.')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sesión cerrada correctamente.')
    return redirect(url_for('landing'))