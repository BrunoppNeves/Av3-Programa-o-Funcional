from flask import Flask, request, g
import mysql.connector
from models import create_tables
import bcrypt

app = Flask(__name__)


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            port='3306',
            password='12345678',
            database='agencia_de_viagens'
        )
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    return "Hello, World!"


@app.route("/<string:table>", methods=["GET"])
def get_data(table):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()

        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")
        senha = data.get("senha")

        if email and senha:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                f"SELECT * FROM passageiro WHERE email = '{email}'"
            )
            passageiro = cursor.fetchone()

            if passageiro:
                # Verifique a senha criptografada usando bcrypt.checkpw
                if bcrypt.checkpw(senha.encode('utf-8'), passageiro['senha'].encode('utf-8')):
                    return {"message": "Login bem-sucedido"}, 200
                else:
                    return {"error": "Credenciais inválidas"}, 401
            else:
                return {"error": "Usuário não encontrado"}, 404
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/passageiro", methods=["POST"])
def create_passageiro():
    try:
        data = request.json
        nome = data.get("nome")
        cpf = data.get("cpf")
        email = data.get("email")
        senha = data.get("senha")

        if nome and cpf and email and senha:
            hashed_password = bcrypt.hashpw(
                senha.encode('utf-8'), bcrypt.gensalt())

            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO passageiro (nome, cpf, email, senha) VALUES (%s, %s, %s, %s)",
                (nome, cpf, email, hashed_password)
            )
            db.commit()
            return {"message": "Passageiro adicionado"}, 201
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/passageiro/<string:idPassageiro>", methods=["GET"])
def get_passageiro(idPassageiro):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM passageiro WHERE id = {idPassageiro}")
        data = cursor.fetchall()

        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/passageiro/<string:idPassageiro>", methods=["PATCH"])
def update_passageiro(idPassageiro):
    cursor = None
    try:
        passageiro = get_passageiro(idPassageiro)
        if len(passageiro) <= 0:
            return {"error": "Passageiro não encontrado"}, 404

        data = request.json
        nome = data.get("nome") if data.get(
            "nome") else passageiro[0].get("nome")
        cpf_novo = data.get("cpf") if data.get(
            "cpf") else passageiro[0].get("cpf")

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE passageiro SET nome = '{nome}', cpf = '{cpf_novo}' WHERE id = {idPassageiro}"
        )
        db.commit()
        passageiro_novo = get_passageiro(idPassageiro)
        return {"message": "Passageiro atualizado", "data": passageiro_novo}, 200
    except mysql.connector.Error as err:
        print("deu erro")
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()


@app.route("/passageiro/<string:idPassageiro>", methods=["DELETE"])
def delete_passageiro(idPassageiro):
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"DELETE FROM passageiro WHERE id = {idPassageiro}")
        db.commit()
        return {"message": "Passageiro deletado"}, 200
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()


if __name__ == "__main__":
    with app.app_context():
        create_tables(get_db().cursor())
    app.run(debug=True)
