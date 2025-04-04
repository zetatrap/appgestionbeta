import sqlite3

def conectar_db():
    conn = sqlite3.connect('mi_aplicacion.db')
    cursor = conn.cursor()
    
    # Crear tablas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT,
        telefono TEXT
    )
    ''')

    # Modificación de la tabla stock
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_producto TEXT NOT NULL,
        cantidad INTEGER,
        precio REAL,
        minimo INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        fecha_emision TEXT,
        fecha_entrega TEXT,
        sena REAL,
        indicaciones TEXT,
        imagen BLOB,
        estado TEXT DEFAULT 'diseño',
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        descripcion TEXT,
        categoria TEXT,
        monto REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        stock_id INTEGER,
        cantidad INTEGER,
        precio REAL,
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY(stock_id) REFERENCES stock(id)
    )
    ''')


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movimientos_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TEXT NOT NULL,
    movimiento TEXT NOT NULL
    );
    ''')


    conn.commit()
    conn.close()

def obtener_conexion():
    return sqlite3.connect('mi_aplicacion.db')

