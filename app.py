from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)


class Manager:

    def __init__(self):
        self.account = 0
        self.warehouse = {}
        self.history = []


manager = Manager()

@app.route('/', methods=["GET", "POST"])
def print_data():
    exit_data = {
    "warehouse": manager.warehouse,
    "account": manager.account,
    }
    return render_template("index.html", context=exit_data)

@app.route('/zakup/', methods=["GET", "POST"])
def get_data_zakup():
    error = '<h1>Zle dane dla zakup!</h1>'
    if request.method == "POST":
        x = request.form.get('product_buy')
        y = request.form.get('price_buy')
        z = request.form.get('product_quantity_buy')
        if x and y and z:
            return redirect(url_for("zakup", product_buy=x, price_buy=y, product_quantity_buy=z))
        else: return error
    else: return error

@app.route('/sprzedaz/', methods=["GET", "POST"])
def get_data_sprzedaz():
    error = '<h1>Zle dane dla sprzedaz!</h1>'
    if request.method == "POST":
        x = request.form.get('product')
        y = request.form.get('price')
        z = request.form.get('product_quantity')
        if x and y and z:
            return redirect(url_for("sprzedaz", product=x, price=y, product_quantity=z))
        else: return error
    else: return error

@app.route('/saldo/', methods=["GET", "POST"])
def get_data_saldo():
    error = '<h1>Zle dane dla saldo!</h1>'
    if request.method == "POST":
        x = request.form.get('comment')
        y = request.form.get('value')
        if x and y:
            return redirect(url_for("saldo", comment=x, value=y))
        else: return error
    else: return error

@app.route('/zakup/<product_buy>/<price_buy>/<product_quantity_buy>/', methods=["GET", "POST"])
def zakup(product_buy, price_buy, product_quantity_buy):
    input_list_zakup = ["zakup", product_buy, price_buy, product_quantity_buy]
    price_buy = int(price_buy)
    if price_buy < 0:
        return '<h1>Ujemna cena!</h1>'
    product_quantity_buy = int(product_quantity_buy)
    if product_quantity_buy < 0:
        return '<h1>Zla ilosc!</h1>'
    if manager.account < product_quantity_buy*price_buy:
        return '<h1>Za malo srodkow!</h1>'
    manager.account -= product_quantity_buy*price_buy
    if product_buy in manager.warehouse:
        manager.warehouse[product_buy] += product_quantity_buy
    else:
        manager.warehouse[product_buy] = product_quantity_buy
    manager.history.append(input_list_zakup)  
    with open('result.txt', "w") as file:
        for item in manager.history:
            file.write(str(item) + "\n")
    return redirect(url_for("print_data"))

@app.route('/sprzedaz/<product>/<price>/<product_quantity>/', methods=["GET", "POST"])
def sprzedaz(product, price, product_quantity):
    input_list_sprzedaz = ["sprzedaz", product, price, product_quantity]
    product_quantity = int(product_quantity)
    if not manager.warehouse:
        return '<h1>Pusty magazym!</h1>'
    if not product in manager.warehouse or manager.warehouse[product] < product_quantity:
        return '<h1>Brak towaru w magazynie!</h1>'
    price = int(price)
    if price < 0:
        return '<h1>Ujemna cena!</h1>'
    if product_quantity < 0:
        return '<h1>Zla ilosc!</h1>'
    manager.account += product_quantity*price
    manager.warehouse[product] -= product_quantity
    if manager.warehouse[product] == 0:
            del manager.warehouse[product]
    manager.history.append(input_list_sprzedaz)
    with open('result.txt', "w") as file:
        for item in manager.history:
            file.write(str(item) + "\n")
    return redirect(url_for("print_data"))

@app.route('/saldo/<value>/<comment>/', methods=["GET", "POST"])
def saldo(value, comment):
    input_list_saldo = ["saldo", value, comment]   
    value = int(value)
    if manager.account + value < 0:
        return '<h1>Brak srodkow</h1>'
    manager.account += value
    manager.history.append(input_list_saldo)
    with open('result.txt', "w") as file:
        for item in manager.history:
            file.write(str(item) + "\n")
    return redirect(url_for("print_data"))

@app.route("/historia/<line_from>/<line_to>/")
def get_history_data(line_from, line_to):
    if line_from <= line_to: 
        a = int(line_from)
        b = int(line_to)     
        if len(manager.history) < b:
            return '<h1>Podany zakres przekracza ilosc zapisanych akcji!</h1>'
        else:
            history = []
            with open("result.txt" , "r") as file:
                for line in file:
                    history.append(line)
            interval = {
                "a" : a,
                "b" : b,
                "history" : history
            }
            return render_template("historia.html", context=interval)
    return '<h1>Zle podane wartosci przedzialu!</h1>'

@app.route("/historia/")
def get_history_data_all():
    history = []
    with open("result.txt" , "r") as file:
        for line in file:
            history.append(line)
    interval = {
        "a" : 0,
        "b" : len(history),
        "history" : history
    }
    return render_template("historia.html", context=interval)