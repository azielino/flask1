from flask import Flask, render_template, request

app = Flask(__name__)

def moja_funkcja():
    return "test"

@app.route("/", methods=["GET", "POST"])
def hello_world():
    name = request.form.get('name')
    context = {
        "name": name,
        "city": moja_funkcja()
    }
    return render_template("index.html", context=context)


@app.route("/historia/<index_start>/<index_stop>")
def history(index_start, index_stop):
    context = {
        "name": "Adam",
        "start": index_start,
        "stop": index_stop
    }
    return render_template("historia.html", context=context)
