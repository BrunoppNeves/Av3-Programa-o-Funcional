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

        # FUNCIONAL: uso do functor map
        remove_pass = lambda u: u.pop('senha')
        if table == "passageiro":
            list(map(remove_pass, data))
            
        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()

# -------------------------------------->   LOGIN    <--------------------------------------


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # FUNCIONAL: uso de um monad
    def maybe_bind(email, senha, f):
        if not senha or not email:
            return {"error": "Dados inválidos"}, 400
        else:
            return f(email, senha)
    
    def maybe(email, senha):
        return lambda f: maybe_bind(email, senha, f)

    def safe_login(email, senha):
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
        
    result = maybe(email, senha)(safe_login)
    cursor.close()
    return result
       

# -------------------------------------->   PASSAGEIRO    <--------------------------------------


@app.route("/passageiro", methods=["POST"])
def create_passageiro():
    try:
        data = request.json
        nome = data.get("nome")
        cpf = data.get("cpf")
        email = data.get("email")
        senha = data.get("senha")

        if nome and cpf and email and senha:
            
            # FUNCIONAL: sucessivas chamadas de funções lambda utilizando currying
            hash_pass = lambda p: lambda r: bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt(rounds=r))
            hashed_password = hash_pass(senha)(12)

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
            f"SELECT id, nome, cpf, email FROM passageiro WHERE id = {idPassageiro}")
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

@app.route("/passageiro/<string:idPassageiro>/voo", methods=["GET"])
def get_passageiro_voo(idPassageiro):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT v.* FROM voo v JOIN voo_has_passageiro vp ON v.id = vp.voo_id WHERE vp.passageiro_id = {idPassageiro};")
        data = cursor.fetchall()

        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()

# -------------------------------------->   CIA AÉREA    <--------------------------------------
@app.route("/cia_aerea", methods=["POST"])
def create_ciaaerea():
    try:
        data = request.json
        nome = data.get("nome")

        if nome:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO cia_aerea (nome) VALUES (%s)",
                (nome,)
            )
            db.commit()
            return {"message": "Cia Aérea adicionada"}, 201
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/cia_aerea/<string:idCiaaerea>", methods=["GET"])
def get_ciaaerea(idCiaaerea):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM cia_aerea WHERE id = {idCiaaerea}")
        data = cursor.fetchall()

        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/cia_aerea/<string:idCiaaerea>", methods=["PATCH"])
def update_ciaaerea(idCiaaerea):
    cursor = None
    try:
        ciaaerea = get_ciaaerea(idCiaaerea)
        if len(ciaaerea) <= 0:
            return {"error": "Cia aérea não encontrada"}, 404

        data = request.json
        nome = data.get("nome") if data.get(
            "nome") else ciaaerea[0].get("nome")

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE cia_aerea SET nome = '{nome}' WHERE id = {idCiaaerea}"
        )
        db.commit()
        ciaaerea_nova = get_ciaaerea(idCiaaerea)
        return {"message": "Cia aérea atualizada", "data": ciaaerea_nova}, 200
    except mysql.connector.Error as err:
        print("deu erro")
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()


@app.route("/cia_aerea/<string:idCiaaerea>", methods=["DELETE"])
def delete_ciaaerea(idCiaaerea):
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"DELETE FROM cia_aerea WHERE id = {idCiaaerea}")
        db.commit()
        return {"message": "Cia aérea deletada"}, 200
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()

# -------------------------------------->   CIDADE    <--------------------------------------


@app.route("/cidade", methods=["POST"])
def create_cidade():
    try:
        data = request.json
        nome = data.get("nome")

        if nome:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO cidade (nome) VALUES (%s)",
                (nome,)
            )
            db.commit()
            return {"message": "Cidade adicionada"}, 201
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/cidade/<string:idCidade>", methods=["GET"])
def get_cidade(idCidade):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM cidade WHERE id = {idCidade}")
        data = cursor.fetchall()

        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/cidade/<string:idCidade>", methods=["PATCH"])
def update_cidade(idCidade):
    cursor = None
    try:
        cidade = get_cidade(idCidade)
        if len(cidade) <= 0:
            return {"error": "Cidade não encontrada"}, 404

        data = request.json
        nome = data.get("nome") if data.get(
            "nome") else cidade[0].get("nome")

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE cidade SET nome = '{nome}' WHERE id = {idCidade}"
        )
        db.commit()
        cidade_nova = get_cidade(idCidade)
        return {"message": "Cidade atualizada", "data": cidade_nova}, 200
    except mysql.connector.Error as err:
        print("deu erro")
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()


@app.route("/cidade/<string:idCidade>", methods=["DELETE"])
def delete_cidade(idCidade):
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"DELETE FROM cidade WHERE id = {idCidade}")
        db.commit()
        return {"message": "Cidade deletada"}, 200
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()

# -------------------------------------->   AEROPORTO    <--------------------------------------


@app.route("/aeroporto", methods=["POST"])
def create_aeroporto():
    try:
        data = request.json
        cidade_id = data.get("cidade_id")
        nome = data.get("nome")

        if cidade_id and nome:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO aeroporto (cidade_id, nome) VALUES (%s, %s)",
                (cidade_id, nome,)
            )
            db.commit()
            return {"message": "Aeroporto adicionado"}, 201
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/aeroporto/<string:idAeroporto>", methods=["GET"])
def get_aeroporto(idAeroporto):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM aeroporto WHERE id = {idAeroporto}")
        data = cursor.fetchall()

        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/aeroporto/<string:idAeroporto>", methods=["PATCH"])
def update_aeroporto(idAeroporto):
    cursor = None
    try:
        aeroporto = get_aeroporto(idAeroporto)
        if len(aeroporto) <= 0:
            return {"error": "Aeroporto não encontrado"}, 404

        data = request.json
        cidade_id = data.get("cidade_id") if data.get(
            "cidade_id") else aeroporto[0].get("cidade_id")
        nome = data.get("nome") if data.get(
            "nome") else aeroporto[0].get("nome")

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE aeroporto SET cidade_id = '{cidade_id}', nome = '{nome}' WHERE id = {idAeroporto}"
        )
        db.commit()
        aeroporto_novo = get_aeroporto(idAeroporto)
        return {"message": "Aeroporto atualizado", "data": aeroporto_novo}, 200
    except mysql.connector.Error as err:
        print("deu erro")
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()


@app.route("/aeroporto/<string:idAeroporto>", methods=["DELETE"])
def delete_aeroporto(idAeroporto):
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"DELETE FROM aeroporto WHERE id = {idAeroporto}")
        db.commit()
        return {"message": "Aeroporto deletado"}, 200
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()

# -------------------------------------->   VOO    <--------------------------------------


@app.route("/voo", methods=["POST"])
def create_voo():
    try:
        data = request.json
        origem = data.get("origem")
        destino = data.get("destino")
        cia_aerea_id = data.get("cia_aerea_id")
        horario = data.get("horario")
        valor = data.get("valor")
        vagas = data.get("vagas")

        if origem and destino and cia_aerea_id and horario:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO voo (origem, destino, cia_aerea_id, horario, valor, vagas) VALUES (%s, %s, %s, %s, %s, %s)",
                (origem, destino, cia_aerea_id, horario, valor, vagas,)
            )
            db.commit()
            return {"message": "Voo adicionado"}, 201
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/voo/<string:idVoo>", methods=["GET"])
def get_voo(idVoo):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM voo WHERE id = {idVoo}")
        data = cursor.fetchall()

        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()


@app.route("/voo/<string:idVoo>", methods=["PATCH"])
def update_voo(idVoo):
    cursor = None
    try:
        voo = get_voo(idVoo)
        if len(voo) <= 0:
            return {"error": "Voo não encontrado"}, 404

        data = request.json
        origem = data.get("origem") if data.get(
            "origem") else voo[0].get("origem")
        destino = data.get("destino") if data.get(
            "destino") else voo[0].get("destino")
        cia_aerea_id = data.get("cia_aerea_id") if data.get(
            "cia_aerea_id") else voo[0].get("cia_aerea_id")
        horario = data.get("horario") if data.get(
            "horario") else voo[0].get("horario")        
        valor = data.get("valor") if data.get(
            "valor") else voo[0].get("valor")
        vagas = data.get("vagas") if data.get(
            "vagas") else voo[0].get("vagas")        

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"UPDATE voo SET origem = '{origem}', destino = '{destino}', cia_aerea_id = '{cia_aerea_id}', horario = '{horario}', valor = '{valor}', vagas = '{vagas}' WHERE id = {idVoo}"
        )
        db.commit()
        voo_novo = get_voo(idVoo)
        return {"message": "Voo atualizado", "data": voo_novo}, 200
    except mysql.connector.Error as err:
        print("deu erro")
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()


@app.route("/voo/<string:idVoo>", methods=["DELETE"])
def delete_voo(idVoo):
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            f"DELETE FROM voo WHERE id = {idVoo}")
        db.commit()
        return {"message": "Voo deletado"}, 200
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        if cursor:
            cursor.close()

# -->   PASSAGEIRO/VOO    <--

@app.route("/voo/<string:idVoo>/passageiro/<string:idPassageiro>", methods=["POST"])
def add_voo_passageiro(idVoo, idPassageiro):
    try:
        if idPassageiro and idVoo:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO voo_has_passageiro (passageiro_id, voo_id) VALUES (%s, %s)",
                (idPassageiro, idVoo,)
            )
            db.commit()
            return {"message": "Passageiro adicionado no voo"}, 201
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()

@app.route("/voo/<string:idVoo>/passageiro", methods=["GET"])
def get_voo_passageiro(idVoo):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT p.id, p.nome, p.cpf FROM passageiro p JOIN voo_has_passageiro vp ON p.id = vp.passageiro_id WHERE vp.voo_id = {idVoo};")
        data = cursor.fetchall()

        # FUNCIONAL: dicionário dentro do escopo (no parâmetro) de uma função lambda
        hide_cpf = lambda p: p["cpf"][0] + '*' * (len(p["cpf"]) - 2) + p["cpf"][-1] if len(p["cpf"]) > 2 else p["cpf"]

        # FUNCIONAL: List Comprehension dentro do escopo de uma Lambda
        encode_data = lambda l: [{'id': p['id'], 'nome': p['nome'], 'cpf': hide_cpf(p)} for p in l]

        data = encode_data(data)
        return data
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()

@app.route("/voo/<string:idVoo>/passageiro/<string:idPassageiro>", methods=["DELETE"])
def remove_voo_passageiro(idVoo, idPassageiro):
    try:
        if idPassageiro and idVoo:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "DELETE FROM voo_has_passageiro WHERE voo_id = %s AND passageiro_id = %s",
                (idVoo, idPassageiro,)
            )
            db.commit()
            return {"message": "Passageiro removido do voo"}, 201
        else:
            return {"error": "Dados inválidos"}, 400
    except mysql.connector.Error as err:
        return {"error": f"Error: {err}"}, 500
    finally:
        cursor.close()

if __name__ == "__main__":
    with app.app_context():
        # FUNCIONAL: função lambda de alta ordem
        create_tables(lambda query: get_db().cursor().execute(query))
    app.run(debug=True)
