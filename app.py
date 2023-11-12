from flask import Flask, request
import mysql.connector

app = Flask(__name__)

# CONEXÃO COM O BANCO
conn = mysql.connector.connect(host='mysql', user='root', password='12345678', database='agencia_de_viagens')
cursor = conn.cursor()

# CRIAÇÃO DAS TABELAS
from models import create_tables
create_tables(cursor)
conn.commit()

# ROTA TESTE
@app.route("/")
def home():
    return "Hello, World!"

# GET PARA TODAS AS TABELAS
@app.route("/<string:table>", methods=["GET"])
def get_data(table):
    try:
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()

        column_names = [column[0] for column in cursor.description]
        result = []
        for row in data:
            result.append({column_names[i]: row[i] for i in range(len(column_names))})

        return result
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500

# POST PASSAGEIRO
@app.route("/passageiro", methods=["POST"])
def create_passageiro():
    data = request.json
    nome = data.get("nome")
    cpf = data.get("cpf")

    if nome and cpf:
        cursor.execute("INSERT INTO passageiro (nome, cpf) VALUES (%s, %s)", (nome, cpf))
        conn.commit()
        return {"message": "Passageiro adicionado"}, 201
    else:
        return {"error": "Dados inválidos"}, 400



if __name__ == "__main__":
    app.run(debug=True)
