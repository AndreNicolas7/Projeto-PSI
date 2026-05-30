from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "segredo"

DATABASE = os.path.join(os.path.dirname(__file__), "banco.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            endereco TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS roupas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tamanho TEXT NOT NULL,
            estado TEXT NOT NULL,
            descricao TEXT NOT NULL,
            usuario TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def obter_usuario(nome, senha=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if senha is None:
        cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (nome,))
    else:
        cursor.execute("SELECT * FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
    usuario = cursor.fetchone()
    conn.close()
    return usuario


def usuario_existente(nome, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE nome = ? OR email = ?",
        (nome, email),
    )
    usuario = cursor.fetchone()
    conn.close()
    return usuario

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    erro = None
    nome = endereco = email = ""

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        endereco = request.form.get("endereco", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        if not nome or not endereco or not email or not senha:
            erro = "Todos os campos são obrigatórios."
            return render_template(
                "cadastro.html",
                erro=erro,
                nome=nome,
                endereco=endereco,
                email=email,
            )

        if usuario_existente(nome, email):
            erro = "Nome de usuário ou e-mail já cadastrado."
            return render_template(
                "cadastro.html",
                erro=erro,
                nome=nome,
                endereco=endereco,
                email=email,
            )

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, endereco, email, senha) VALUES (?, ?, ?, ?)",
            (nome, endereco, email, senha),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    nome = ""

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "").strip()

        if not nome or not senha:
            erro = "Informe nome e senha."
            return render_template("login.html", erro=erro, nome=nome)

        usuario = obter_usuario(nome, senha)
        if usuario:
            session["usuario"] = usuario["nome"]
            return redirect(url_for("index"))

        erro = "Nome ou senha inválidos."

    return render_template("login.html", erro=erro, nome=nome)

@app.route("/cadastro_roupa", methods=["GET", "POST"])
def cadastro_roupa():
    if not session.get("usuario"):
        return redirect(url_for("login"))

    erro = None
    nome = tamanho = estado = descricao = ""

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        tamanho = request.form.get("tamanho", "").strip()
        estado = request.form.get("estado", "").strip()
        descricao = request.form.get("descricao", "").strip()

        if not nome or not tamanho or not estado or not descricao:
            erro = "Todos os campos são obrigatórios."
            return render_template(
                "cadastro_roupa.html",
                erro=erro,
                nome=nome,
                tamanho=tamanho,
                estado=estado,
                descricao=descricao,
            )

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO roupas (nome, tamanho, estado, descricao, usuario) VALUES (?, ?, ?, ?, ?)",
            (nome, tamanho, estado, descricao, session["usuario"]),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("catalogo", usuario=session["usuario"]))

    return render_template("cadastro_roupa.html")

@app.route("/catalogo")
def catalogo():
    if not session.get("usuario"):
        return redirect(url_for("login"))

    usuario = request.args.get("usuario") or session["usuario"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roupas WHERE usuario = ?", (usuario,))
    roupas = cursor.fetchall()
    conn.close()

    return render_template("catalogo.html", roupas=roupas, usuario=usuario)


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("index"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if request.method == "POST":
        for roupa in roupas:
            if int(roupa["id"]) == id:
                roupa["nome"] = request.form.get("nome")
                roupa["tamanho"] = request.form.get("tamanho")
                roupa["estado"] = request.form.get("estado")
                roupa["descricao"] = request.form.get("descricao")

                return redirect(url_for("catalogo", usuario = session.get('usuario')))
            
    roupa = None

    for r in roupas:
        if r["id"] == id:
            roupa = r
            break

    if roupa is None:
        return redirect(url_for("catalogo", usuario = session.get('usuario')))

    return render_template("editar.html", roupa=roupa)

@app.route("/remover_roupa/<int:id>", methods=["POST"])
def remover_roupa(id):
    remover = request.form.get("remover")
    if remover == "REMOVER":
        for roupa in roupas:
            if roupa["id"] == id:
                roupas.remove(roupa)
                break
        return redirect(url_for("catalogo", usuario = session.get('usuario')))
    return redirect(url_for("catalogo", usuario = session.get('usuario')))
