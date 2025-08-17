import sqlite3, os
from flask import g

DB_PATH = "thaipoint.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def close_connection(app):
    @app.teardown_appcontext
    def close(exc):
        db = getattr(g, "_database", None)
        if db is not None:
            db.close()

def init_db():
    if os.path.exists(DB_PATH):
        return
    db = get_db()
    c = db.cursor()
    # Tabelas
    c.execute("""
    CREATE TABLE stores (
        id TEXT PRIMARY KEY, name TEXT, bairro TEXT, type TEXT,
        rating REAL, delivery_fee REAL, min_time INT, max_time INT
    )""")
    c.execute("""
    CREATE TABLE products (
        id TEXT PRIMARY KEY, store_id TEXT, name TEXT, price REAL
    )""")
    c.execute("""
    CREATE TABLE orders (
        id TEXT PRIMARY KEY, store_id TEXT, type TEXT, address TEXT,
        status TEXT, eta TIMESTAMP, subtotal REAL, delivery_fee REAL, total REAL
    )""")
    c.execute("""
    CREATE TABLE order_items (
        order_id TEXT, product_id TEXT, name TEXT, price REAL, qty INT
    )""")
    # Dados iniciais
    stores = [
        ("1","Mercadão do Centro","Centro","Supermercado",4.7,5.9,12,28),
        ("2","Açaí da Orla","Beira Rio","Lanchonete",4.8,3.5,10,20),
    ]
    products = [
        ("p1","1","Arroz 5kg",29.9),("p2","1","Feijão 1kg",8.9),
        ("p3","1","Café 500g",12.5),("p4","1","Óleo 900ml",7.9),
        ("p5","2","Açaí 300ml",10.0),("p6","2","Açaí 500ml",14.0),
        ("p7","2","Tapioca de Queijo",8.0)
    ]
    c.executemany("INSERT INTO stores VALUES (?,?,?,?,?,?,?,?)", stores)
    c.executemany("INSERT INTO products VALUES (?,?,?,?)", products)
    db.commit()
