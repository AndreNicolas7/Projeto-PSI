from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/cadastro_roupa")
def cadastro_roupa():
    return render_template("cadastro_roupa.html")

@app.route("/catalogo")
def catalogo():
    return render_template("catalogo.html")

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route("/carrinho")
def carrinho():
    return render_template("carrinho.html")