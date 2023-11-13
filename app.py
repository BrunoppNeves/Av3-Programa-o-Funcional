from flask import Flask, request, g
import mysql.connector
from models import create_tables

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


@app.route("/passageiro", methods=["POST"])
def create_passageiro():
    try:
        data = request.json
        nome = data.get("nome")
        cpf = data.get("cpf")

        if nome and cpf:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO passageiro (nome, cpf) VALUES (%s, %s)", (nome, cpf))
            db.commit()
            return {"message": "Passageiro adicionado"}, 201
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/passageiro/<string:cpf>", methods=["GET"])
def get_passageiro(cpf):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM passageiro WHERE cpf = '{cpf}'")
        data = cursor.fetchall()

        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/passageiro/<string:cpf>", methods=["PUT"])
def update_passageiro(cpf):
    try:
        data = request.json
        nome = data.get("nome")
        cpf_novo = data.get("cpf")

        if nome and cpf:
            passageiro = get_passageiro(cpf)
            if not passageiro:
                return {"error": "Passageiro não encontrado"}, 404

            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                f"UPDATE passageiro SET nome = '{nome}', cpf = '{cpf_novo}' WHERE id = {passageiro[0]['id']}"
            )
            db.commit()

            passageiro_novo = get_passageiro(cpf_novo)
            return {"message": "Passageiro atualizado", "data": passageiro_novo}, 200
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/passageiro/<string:cpf>", methods=["DELETE"])
def delete_passageiro(cpf):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"DELETE FROM passageiro WHERE cpf = '{cpf}'")
        db.commit()
        return {"message": "Passageiro deletado"}, 200
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


if __name__ == "__main__":
    with app.app_context():
        create_tables(get_db().cursor())
    app.run(debug=True)
