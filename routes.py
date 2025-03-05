from flask import render_template, redirect, url_for, request, flash, session
from app import app
from models import Usuario, db
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = Usuario(username=username, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso! Por favor inicia sesión.','success')
            return redirect(url_for('login'))
        except:
            flash('El nombre de usuario ya está en uso.','warning')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = username
            flash('Inicio de sesión exitoso!','success')
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos.','danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Por favor inicia sesión para acceder al dashboard.', 'danger')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sesión cerrada correctamente.','success')
    return redirect(url_for('landing'))

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if request.method == 'POST':
        email = request.form['email']
        telefono = request.form['telefono']
        nombre_comercio = request.form['comercio'] 
        user_id = session['user_id']
        user = Usuario.query.filter_by(id=user_id).first()
        try:
            #TODO: ver si uso modelo usuario o creo otro
            #db.session.add(user)
            #db.session.commit()
            flash('Cambios guardados con éxito','success')
        except:
            flash('Error al guardar cambios','danger')
    return render_template('configuracion.html')
