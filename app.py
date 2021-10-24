from flask import Flask, render_template, request, url_for, redirect
from definitions import manager, history_to_str

app = Flask(__name__)

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
        x = request.form.get('comment'),
        y = request.form.get('value')
        if x and y:
            return redirect(url_for("saldo", comment=x, value=y))
        else: return error
    else: return error

@app.route('/zakup/<product_buy>/<price_buy>/<product_quantity_buy>/', methods=["GET", "POST"])
def zakup(product_buy, price_buy, product_quantity_buy):
    input_list_zakup = ["zakup", product_buy, price_buy, product_quantity_buy]
    price_buy = int(price_buy)
    product_quantity_buy = int(product_quantity_buy)
    manager.account -= product_quantity_buy*price_buy
    if product_buy in manager.warehouse:
        manager.warehouse[product_buy] += product_quantity_buy
    else:
        manager.warehouse[product_buy] = product_quantity_buy
    manager.history.append(input_list_zakup)  
    history_str = history_to_str(manager.history)
    with open('result.txt', "w") as file:
        for item in history_str:
            file.write(item + "\n")
    return redirect(url_for("print_data"))

@app.route('/sprzedaz/<product>/<price>/<product_quantity>/', methods=["GET", "POST"])
def sprzedaz(product, price, product_quantity):
    input_list_sprzedaz = ["sprzedaz", product, price, product_quantity]
    product_quantity = int(product_quantity)
    if manager.warehouse:
        if product in manager.warehouse and manager.warehouse[product] >= product_quantity:
            price = int(price)
            if price >= 0:
                if product_quantity > 0:
                    manager.account += product_quantity*price
                    manager.warehouse[product] -= product_quantity
                    if manager.warehouse[product] == 0:
                            del manager.warehouse[product]
                    manager.history.append(input_list_sprzedaz)
                    history_str = history_to_str(manager.history)
                    with open('result.txt', "w") as file:
                        for item in history_str:
                            file.write(item + "\n")
    return redirect(url_for("print_data"))

@app.route('/saldo/<value>/<comment>/', methods=["GET", "POST"])
def saldo(value, comment):
    input_list_saldo = ["saldo", value, comment]   
    value = int(value)
    manager.account += value
    manager.history.append(input_list_saldo)
    history_str = history_to_str(manager.history)
    with open('result.txt', "w") as file:
        for item in history_str:
            file.write(item + "\n")
    return redirect(url_for("print_data"))



# @app.route("/historia/<index_start>/<index_stop>")
# def history(index_start, index_stop):
#     context = {
#         "name": "Adam",
#         "start": index_start,
#         "stop": index_stop
#     }
#     return render_template("historia.html", context=context)


