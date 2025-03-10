from flask_sqlalchemy import SQLAlchemy

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    nombre_comercio = db.Column(db.String(150), nullable=True)
    numero = db.Column(db.String(150), nullable=True)
    plantilla_wsp = db.Column(db.Integer)
    
    proveedores = db.relationship('Proveedor', backref='usuario', lazy=True)
    definiciones = db.relationship('Definicion', backref='usuario', lazy=True)

# Modelo de Proveedor
class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    nombre = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    leap_time = db.Column(db.Integer, nullable=False)  # Tiempo de entrega en días
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    productos = db.relationship('Producto', backref='proveedor', lazy=True)
    pedidos = db.relationship('Pedido', backref='proveedor', lazy=True)

# Modelo de Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    unidades = db.Column(db.String(10), nullable=False, default='Kg')
    rop = db.Column(db.Integer, nullable=False)  # Punto de reorden
    lote = db.Column(db.Integer, nullable=False) # Tamaño del lote de compra
    
    pedidos = db.relationship('PedidoProducto', back_populates='producto', lazy=True)
    movimientos_stock = db.relationship('MovimientoStock', backref='producto', lazy=True)

    @property
    def stock_actual(self):
        return sum(mov.cantidad for mov in self.movimientos_stock)
# Modelo de Pedido
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    
    productos = db.relationship('PedidoProducto', back_populates='pedido', cascade='all, delete-orphan', lazy=True)

# Tabla intermedia para la relación One-to-Many entre Pedido y Producto
class PedidoProducto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad_pedida = db.Column(db.Integer, nullable=False)
    
    pedido = db.relationship('Pedido', back_populates='productos')
    producto = db.relationship('Producto', back_populates='pedidos')

# Modelo de Definiciones
class Definicion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    autom = db.Column(db.Boolean, default=False)  
    dias = db.Column(db.Integer, default=14)
    menor = db.Column(db.Boolean, default=True)   

# Modelo de Movimiento de Stock
class MovimientoStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
