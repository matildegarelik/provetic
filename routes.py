from flask import render_template, redirect, url_for, request, flash, session
from app import app
from models import Usuario, db, Definicion, Proveedor, MovimientoStock, Producto
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sqlalchemy import desc
from datetime import datetime

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
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))  

    user_id = session['user_id']
    user = Usuario.query.filter_by(id=user_id).first()

    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('landing'))  

    if request.method == 'POST':
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        nombre_comercio = request.form.get('comercio')
        plantilla = request.form.get('plantilla')

        try:
            user.email = email
            user.numero = telefono  
            user.nombre_comercio = nombre_comercio
            user.plantilla_wsp = plantilla

            db.session.commit()
            flash('Cambios guardados con éxito', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar cambios: {str(e)}', 'danger')

    return render_template('configuracion.html', usuario=user)

@app.route('/definiciones', methods=['GET', 'POST'])
def definiciones():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))  

    user_id = session['user_id']
    user = Usuario.query.filter_by(id=user_id).first()
    definicion = Definicion.query.filter_by(user_id=user_id).first() or Definicion(user_id=user_id)
    
    if not definicion.id:
        db.session.add(definicion)
        db.session.commit()

    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('landing'))  

    if request.method == 'POST':
        autom = request.form.get('autom')
        dias = request.form.get('dias')
        menor = request.form.get('menor')

        try:
            user.autom = autom
            user.dias = dias  
            user.menor = menor

            db.session.commit()
            flash('Cambios guardados con éxito', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar cambios: {str(e)}', 'danger')

    return render_template('definiciones.html', usuario=user, definicion= definicion)

@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        if 'file' in request.files:  # Carga de Excel
            file = request.files['file']
            if file and file.filename.endswith(('.xls', '.xlsx')):
                try:
                    # Cargar el archivo Excel directamente en memoria
                    df = pd.read_excel(file)

                    for _, row in df.iterrows():
                        codigo = row['Codigo Proveedor']
                        nombre = row['Proveedor']
                        email = row.get('Email', None)
                        whatsapp = row.get('whatsapp', None)
                        leap_time = row.get('Leap time', None)

                        if pd.isna(leap_time):
                            leap_time = 0

                        # Verificar duplicados
                        if not Proveedor.query.filter_by(codigo=codigo, nombre=nombre, user_id=user_id).first():
                            proveedor = Proveedor(
                                codigo=codigo,
                                nombre=nombre,
                                email=email if pd.notna(email) else None,
                                whatsapp=whatsapp if pd.notna(whatsapp) else None,
                                leap_time=int(leap_time),
                                user_id=user_id
                            )
                            db.session.add(proveedor)
                        else:
                            flash(f'Proveedor {codigo} - {nombre} ya existe. No se actualizó.', 'warning')

                    db.session.commit()
                    flash('Proveedores cargados exitosamente.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error al cargar el archivo: {str(e)}', 'danger')
     
        elif 'edit_id' in request.form:  # Edición en tabla
            proveedor = Proveedor.query.get(request.form['edit_id'])
            if proveedor and proveedor.user_id == user_id:
                proveedor.codigo = request.form['codigo']
                proveedor.nombre = request.form['nombre']
                proveedor.email = request.form['email'] or None
                proveedor.whatsapp = request.form['whatsapp'] or None
                proveedor.leap_time = int(request.form['leap_time'] or 0)

                try:
                    db.session.commit()
                    flash('Proveedor actualizado correctamente.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error al actualizar proveedor: {str(e)}', 'danger')

        else:  # Creación manual
            codigo = request.form['codigo']
            nombre = request.form['nombre']
            email = request.form['email']
            whatsapp = request.form['whatsapp']
            leap_time = request.form['leap_time']

            proveedor = Proveedor(
                codigo=codigo,
                nombre=nombre,
                email=email,
                whatsapp=whatsapp,
                leap_time=int(leap_time),
                user_id=user_id
            )
            try:
                db.session.add(proveedor)
                db.session.commit()
                flash('Proveedor agregado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al agregar proveedor: {str(e)}', 'danger')

    proveedores = Proveedor.query.filter_by(user_id=user_id).all()
    return render_template('proveedores.html', proveedores=proveedores)

@app.route('/historial_stock')
def historial_stock():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    movimientos = (MovimientoStock.query
        .join(Producto)
        .filter(Producto.proveedor.has(user_id=user_id))
        .order_by(desc(MovimientoStock.fecha))
        .all())
    return render_template('historial_stock.html', movimientos=movimientos)

@app.route('/productos', methods=['GET', 'POST'])
def productos():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        if 'file' in request.files:  
            file = request.files['file']
            if file and file.filename.endswith(('.xls', '.xlsx')):
                try:
                    df = pd.read_excel(file)
                    for _, row in df.iterrows():
                        nombre = row['Producto']
                        nuevo_stock = row['Cantidad']
                        unidades = row['Unidades']
                        codigo_proveedor = row['Codigo proveedor']

                        proveedor = Proveedor.query.filter_by(codigo=codigo_proveedor, user_id=user_id).first()
                        if not proveedor:
                            flash(f'Proveedor {codigo_proveedor} no existe. No se agregó el producto: {nombre}.', 'warning')
                        else:
                            producto = Producto.query.filter_by(nombre=nombre, proveedor_id=proveedor.id).first()
                            if producto:
                                stock_actual = sum(mov.cantidad for mov in producto.movimientos_stock)
                                ajuste = nuevo_stock - stock_actual

                                # Crear un nuevo movimiento para ajustar el stock
                                if ajuste != 0:
                                    movimiento = MovimientoStock(
                                        producto_id=producto.id,
                                        cantidad=ajuste,
                                        fecha=datetime.utcnow()
                                    )
                                    db.session.add(movimiento)
                                    db.session.commit()
                            else:

                                nuevo_producto = Producto(
                                    nombre=nombre,
                                    unidades=unidades,
                                    rop=10,
                                    lote=100,
                                    proveedor_id=int(proveedor.id)
                                )
                                db.session.add(nuevo_producto)
                                db.session.commit()

                                movimiento = MovimientoStock(
                                        producto_id=nuevo_producto.id,
                                        cantidad=nuevo_stock,
                                        fecha=datetime.utcnow()
                                    )
                                db.session.add(movimiento)
                                    
                    db.session.commit()
                    flash('Productos cargados/actualizados correctamente.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error al cargar el archivo: {str(e)}', 'danger')
    productos = Producto.query.join(Proveedor).filter(Proveedor.user_id == user_id).all()
    return render_template('productos.html', productos=productos)

@app.route('/actualizar_producto', methods=['POST'])
def actualizar_producto():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    data = request.json
    producto = Producto.query.get(data['producto_id'])
    if producto:
        producto.rop = int(data['nuevo_rop'])
        producto.lote = int(data['nuevo_lote'])
        db.session.commit()

        stock_actual = sum(mov.cantidad for mov in producto.movimientos_stock)
        ajuste = int(data['nuevo_stock']) - stock_actual

        # Crear un nuevo movimiento para ajustar el stock
        if ajuste != 0:
            movimiento = MovimientoStock(
                producto_id=producto.id,
                cantidad=ajuste,
                fecha=datetime.utcnow()
            )
            db.session.add(movimiento)
            db.session.commit()
        return {'success': True}, 200
    return {'error': 'Producto no encontrado o sin permisos'}, 404

