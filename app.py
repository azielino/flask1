from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///historia.db'
db = SQLAlchemy(app)

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(80), unique=False, nullable=False)
    value = db.Column(db.Integer, unique=False, nullable=False, server_default="", default="")
    comment = db.Column(db.String(120), unique=False, nullable=False, server_default="", default="")
    product = db.Column(db.String(120),unique=False, nullable=False, server_default="", default="")
    price = db.Column(db.Integer,unique=False, nullable=False, server_default="", default="")
    product_quantity = db.Column(db.Integer,unique=False, nullable=False, server_default="", default="")
    account = db.Column(db.Integer, nullable=False,unique=False, server_default="", default="")

db.create_all()

class Manager:

    def __init__(self):
        self.account = self.set_account()
        self.warehouse = self.set_warehouse()

    def set_account(self):
        try:
            return db.session.query(Action).all()[-1].account
        except IndexError:
            return 0

    def set_warehouse(self):
        warehouse = {}
        for item in db.session.query(Action).all():
            if item.product and (item.action == "zakup" or item.action == "sprzedaz"):
                warehouse[f"{item.product}"] = 0
        for item in db.session.query(Action).filter(Action.action=="zakup").all():
            warehouse[f"{item.product}"] += item.product_quantity
        for item in db.session.query(Action).filter(Action.action=="sprzedaz").all():
            warehouse[f"{item.product}"] -= item.product_quantity
            if warehouse[f"{item.product}"] == 0:
                del warehouse[f"{item.product}"]
        return warehouse

    def set_zl_gr(self, y, z):
        if not y:
            y = '0'
        if not z:
            z = '0'
        y = int(y)
        z = int(z)
        if z >= 0 and z <= 99:
            if z < 10:
                z = f'0{z}'
            return f'{y}.{z}'


manager = Manager()

@app.route('/')
def print_data():
    exit_data = {
    "warehouse": manager.warehouse,
    "account": manager.account,
    }
    return render_template("index.html", context=exit_data)

@app.route('/error/<error>')
def error(error):
    error = {"error": error}
    return render_template("error.html", context=error)

@app.route('/zakup/', methods=["GET", "POST"])
def get_data_zakup():
    if request.method == "POST":
        x = request.form.get('product_buy')
        y = request.form.get('price_buy_zl')
        z = request.form.get('price_buy_gr')
        w = request.form.get('product_quantity_buy')
        if x and w:
            q = manager.set_zl_gr(y, z)
            if not q:
                return redirect(url_for("error", error='Zła wartość w groszach!'))
            return redirect(url_for(
                "zakup", product_buy=x, price_buy=q, product_quantity_buy=w)
                )
    return redirect(url_for("error", error='Złe dane dla zakup!'))

@app.route('/sprzedaz/', methods=["GET", "POST"])
def get_data_sprzedaz():
    if request.method == "POST":
        x = request.form.get('product')
        y = request.form.get('price_zl')
        z = request.form.get('price_gr')
        w = request.form.get('product_quantity')
        if x and w:
            q = manager.set_zl_gr(y, z)
            if not q:
                return redirect(url_for("error", error='Zła wartość w groszach!'))
            return redirect(url_for("sprzedaz", product=x, price=q, product_quantity=w))
    return redirect(url_for("error", error='Złe dane dla sprzedaż!'))

@app.route('/saldo/', methods=["GET", "POST"])
def get_data_saldo():
    if request.method == "POST":
        x = request.form.get('comment')
        y = request.form.get('value_zl')
        z = request.form.get('value_gr')
        if x:
            q = manager.set_zl_gr(y, z)
            if not q:
                return redirect(url_for("error", error='Zła wartość w groszach!'))
            return redirect(url_for("saldo", value=q, comment=x))
    return redirect(url_for("error", error='Złe dane dla saldo!'))

@app.route('/historia_od_do/', methods=["GET", "POST"])
def get_data_hisroria_od_do(): 
    if request.method == "POST":
        x = request.form.get('od')
        y = request.form.get('do')
        if x and y:
            return redirect(url_for("get_history_data", line_from=x, line_to=y))
    return redirect(url_for("error", error='Złe dane dla Historia od do!'))

@app.route('/zakup/<product_buy>/<price_buy>/<product_quantity_buy>/', methods=["GET", "POST"])
def zakup(product_buy, price_buy, product_quantity_buy):
    price_buy = float(price_buy)
    if price_buy < 0:
        return redirect(url_for("error", error='Ujemna cena!'))
    product_quantity_buy = int(product_quantity_buy)
    if product_quantity_buy < 0:
        return redirect(url_for("error", error='Zła ilość!'))
    if manager.account < product_quantity_buy*price_buy:
        return redirect(url_for("error", error='Za mało środków!'))
    manager.account -= product_quantity_buy*price_buy
    obj = Action(
        action = "zakup",
        product = product_buy,
        price = price_buy,
        product_quantity = product_quantity_buy,
        account = manager.account
        )
    db.session.add(obj)
    db.session.commit()
    if product_buy in manager.warehouse:
        manager.warehouse[product_buy] += product_quantity_buy
    else:
        manager.warehouse[product_buy] = product_quantity_buy
    return redirect(url_for("print_data"))

@app.route('/sprzedaz/<product>/<price>/<product_quantity>/', methods=["GET", "POST"])
def sprzedaz(product, price, product_quantity):
    product_quantity = int(product_quantity)
    if not manager.warehouse:
        return redirect(url_for("error", error='Pusty magazym!'))
    if not product in manager.warehouse or manager.warehouse[product] < product_quantity:
        return redirect(url_for("error", error='Brak towaru w magazynie!'))
    price = float(price)
    if price < 0:
        return redirect(url_for("error", error='Ujemna cena!'))
    if product_quantity < 0:
        return redirect(url_for("error", error='Zła ilość!'))
    manager.account += product_quantity * price
    obj = Action(
        action = "sprzedaz",
        product = product,
        price = price,
        product_quantity = product_quantity,
        account = manager.account
        )
    db.session.add(obj)
    db.session.commit()
    manager.warehouse[product] -= product_quantity
    if manager.warehouse[product] == 0:
        del manager.warehouse[product]
    return redirect(url_for("print_data"))

@app.route('/saldo/<value>/<comment>/', methods=["GET", "POST"])
def saldo(value, comment):
    value = float(value)
    if manager.account + value < 0:
        return redirect(url_for("error", error='Brak środków!'))
    if not value:
        return redirect(url_for("error", error='Zerowa wpłata!'))
    manager.account += value
    obj = Action(
        action = "saldo",
        value = value,
        comment = comment,
        account = manager.account
        )
    db.session.add(obj)
    db.session.commit()
    return redirect(url_for("print_data"))

@app.route("/historia/<line_from>/<line_to>/")
def get_history_data(line_from, line_to):
    a = int(line_from)
    b = int(line_to)
    if a <= b:
        if len(db.session.query(Action).all()) < b:
            return redirect(url_for(
                "error", error='Podany zakres przekracza ilość zapisanych operacji!')
                )
        else:
            history = []
            for i in range(a, b + 1):
                for item in db.session.query(Action).filter(Action.id==i).all():
                    history.append(item)
            context = {
                "a" : a,
                "b" : b,
                "history" : history
            }
            return render_template("historia.html", context=context)
    return redirect(url_for("error", error='Źle podane wartości przedziału!'))

@app.route("/historia/")
def get_history_data_all():
    context = {
        "a" : None,
        "b" : None,
        "history" : db.session.query(Action).all()
    }
    return render_template("historia.html", context=context)

if __name__ == '__main__':
    app.run()