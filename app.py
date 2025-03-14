from flask import Flask
from models import Usuario, db
from cronjob_pedidos import crear_pedidos_automaticos, crear_pedidos_por_fecha

# Inicialización de la app y configuración
app = Flask(__name__, static_folder='static')
app.secret_key = 'tu_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)

from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Tablas creadas:', db.metadata.tables.keys())
        crear_pedidos_automaticos()  # Llama al cronjob al iniciar
        crear_pedidos_por_fecha()

    app.run(debug=True)
