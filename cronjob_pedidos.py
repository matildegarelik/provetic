from datetime import datetime, timedelta
from models import Usuario, Producto, Pedido, PedidoProducto, Definicion, db
from utils import enviar_mensaje


def crear_pedidos_automaticos():
    usuarios_autom = Usuario.query.join(Definicion).filter(Definicion.autom == True).all()
    procesar_pedidos(usuarios_autom)

def crear_pedidos_por_fecha():
    hoy = datetime.now()
    usuarios_no_autom = Usuario.query.join(Definicion).filter(Definicion.autom == False).all()
    for usuario in usuarios_no_autom:
        definicion = usuario.definiciones[0]
        if usuario.definiciones and usuario.definiciones[0].ult_chequeo + timedelta(days=definicion.dias) <= hoy:
            procesar_pedidos([usuario])
            definicion.ult_chequeo = hoy  # Actualizar ult_chequeo después del pedido
            db.session.commit()

def procesar_pedidos(usuarios):
    for usuario in usuarios:
        for proveedor in usuario.proveedores:
            productos_a_pedir = []
            for producto in proveedor.productos:
                stock_actual = producto.stock_actual
                ultimo_pedido = Pedido.query.join(PedidoProducto).filter(
                    Pedido.proveedor_id == proveedor.id,
                    PedidoProducto.producto_id == producto.id
                ).order_by(Pedido.fecha.desc()).first()
                leap_time_cumplido = True
                if ultimo_pedido:
                    fecha_limite = ultimo_pedido.fecha + timedelta(days=proveedor.leap_time)
                    if fecha_limite > datetime.now():
                        leap_time_cumplido = False

                if leap_time_cumplido and ((producto.rop > stock_actual) if usuario.definiciones[0].menor else (producto.rop >= stock_actual)):
                    productos_a_pedir.append((producto, producto.lote))
            
            if productos_a_pedir:
                nuevo_pedido = Pedido(proveedor_id=proveedor.id, fecha=datetime.now())
                db.session.add(nuevo_pedido)
                db.session.flush()
                
                detalles_pedido = ""
                for producto, cantidad in productos_a_pedir:
                    pedido_producto = PedidoProducto(
                        pedido_id=nuevo_pedido.id,
                        producto_id=producto.id,
                        cantidad_pedida=cantidad
                    )
                    detalles_pedido+=f"{producto.nombre} - Cantidad: {cantidad} {producto.unidades}\n"
                    enviar_mensaje(usuario,detalles_pedido)
                    db.session.add(pedido_producto)
                db.session.commit()

