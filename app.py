from flask import Flask
import mysql.connector
from models import create_tables

app = Flask(__name__)

# CONEXÃO COM O BANCO
conn = mysql.connector.connect(host='mysql', user='root', password='12345678', database='agencia_de_viagens')
cursor = conn.cursor()

# CRIAÇÃO DAS TABELAS
create_tables(cursor)
conn.commit()

@app.route("/")
def home():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)
