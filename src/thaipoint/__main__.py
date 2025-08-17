from flask import Flask, g, render_template_string, request, redirect, url_for, session
from random import randint
from datetime import datetime, timedelta
import uuid
from db import init_db, get_db, close_connection
from templates import APP_TABS_TEMPLATE

app = Flask(__name__)
app.secret_key = "s3cr3t"
close_connection(app)  # fecha db automaticamente

# --- Helpers ---
def fetchall_dict(c):
    return [dict(row) for row in c.fetchall()]

def get_cart():
    return session.get("cart", [])

def save_cart(cart):
    session["cart"] = cart

def get_active_order():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM orders WHERE status!='entregue' ORDER BY eta DESC LIMIT 1")
    order = c.fetchone()
    if order:
        c.execute("SELECT * FROM order_items WHERE order_id=?", (order["id"],))
        order = dict(order)
        order["items"] = fetchall_dict(c)
        return order
    return None

# --- Rotas ---
@app.route("/", methods=["GET","POST"])
def index():
    db = get_db()
    c = db.cursor()
    query = request.form.get("query","")
    bairro = request.form.get("bairro","todos")

    q = "SELECT * FROM stores WHERE 1=1"
    params = []
    if bairro != "todos":
        q += " AND bairro=?"
        params.append(bairro)
    if query:
        q += " AND (name LIKE ? OR type LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    c.execute(q, params)
    stores = fetchall_dict(c)

    for s in stores:
        c.execute("SELECT * FROM products WHERE store_id=?", (s["id"],))
        s["products"] = fetchall_dict(c)

    c.execute("SELECT DISTINCT bairro FROM stores")
    bairros = ["todos"] + [row["bairro"] for row in c.fetchall()]

    active_order = get_active_order()
    progress = 0
    if active_order:
        status_map = {"confirmado":10,"preparando":40,"a_caminho":70,"na_porta":90,"entregue":100}
        progress = status_map.get(active_order["status"],0)

    return render_template_string(APP_TABS_TEMPLATE, stores=stores, cart=get_cart(),
                                  active_order=active_order, bairros=bairros,
                                  selected_bairro=bairro, query=query, progress=progress)

@app.route("/add_to_cart/<store_id>/<product_id>")
def add_to_cart(store_id, product_id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM products WHERE id=?",(product_id,))
    p = c.fetchone()
    if not p:
        return redirect("/")
    cart = get_cart()
    if cart and cart[0]["store_id"]!=store_id:
        cart = []
    for i in cart:
        if i["id"]==product_id:
            i["qty"]+=1
            break
    else:
        cart.append(dict(p))
        cart[-1]["qty"]=1
        cart[-1]["store_id"]=store_id
    save_cart(cart)
    return redirect("/")

@app.route("/remove_item/<product_id>")
def remove_item(product_id):
    cart = get_cart()
    cart = [i for i in cart if i["id"]!=product_id]
    save_cart(cart)
    return redirect("/")

@app.route("/place_order", methods=["POST"])
def place_order():
    cart = get_cart()
    if not cart:
        return redirect("/")
    db = get_db()
    c = db.cursor()
    store_id = cart[0]["store_id"]
    delivery_type = request.form.get("delivery_type","retirada")
    address = request.form.get("address","")
    eta_minutes = randint(10,30)
    order_id = str(uuid.uuid4())
    subtotal = sum(i["price"]*i["qty"] for i in cart)
    delivery_fee = 0 if delivery_type=="retirada" else 5.0
    total = subtotal + delivery_fee
    eta = datetime.now() + timedelta(minutes=eta_minutes)
    c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)",
              (order_id, store_id, delivery_type, address, "confirmado", eta, subtotal, delivery_fee, total))
    for i in cart:
        c.execute("INSERT INTO order_items VALUES (?,?,?,?,?)",
                  (order_id, i["id"], i["name"], i["price"], i["qty"]))
    db.commit()
    save_cart([])  # esvazia carrinho ao finalizar
    return redirect("/")

# --- Run ---
if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host="0.0.0.0", port=8080)
