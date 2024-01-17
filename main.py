from flask import Flask, jsonify, request
import psycopg2
import functions as func

conn = psycopg2.connect(
    host="isabelle.db.elephantsql.com",
    database="zlhwkfxk",
    user="zlhwkfxk",
    password="5H5djg3N01zMeTkRC3RmnZoFVo9Yia63",
)

# Criar um cursor
cursor = conn.cursor()


app = Flask(__name__)


@app.route("/session/add/", methods=["POST"])
def addParticipante():
    participante = request.get_json()

    tableID = participante["tableID"]
    nome = participante["nome"]
    cpf = participante["cpf"]
    desejo = participante["desejo"]
    cpf = func.limpar_cpf(cpf)
    #001-tbid/002-cpf/003-nome/004-desejo/005-cad/
    try:
        if not verificarTableID(tableID):
            return jsonify(
                {
                    "tableID": tableID,
                    "nome": nome,
                    "cpf": cpf,
                    "desejo": desejo,
                    "response": "001"
                }
            )
        elif func.invalidCpf(cpf):
            return jsonify(
                {
                    "tableID": tableID,
                    "nome": nome,
                    "cpf": cpf,
                    "desejo": desejo,
                    "response": "002"
                }
            )
        elif func.invalidValue(nome,2,20):
            return jsonify(
                {
                    "tableID": tableID,
                    "nome": nome,
                    "cpf": cpf,
                    "desejo": desejo,
                    "response": "003"
                }
            )
        elif func.invalidValue(desejo,4,255):
            return jsonify(
                {
                    "tableID": tableID,
                    "nome": nome,
                    "cpf": cpf,
                    "desejo": desejo,
                    "response": "004"
                }
            )
        elif verifyGuest(cpf,tableID):
            return jsonify(
                {
                    "tableID": tableID,
                    "nome": nome,
                    "cpf": cpf,
                    "desejo": desejo,
                    "response": "005"
                }
            )

        cursor.execute(
            f"INSERT INTO \"{tableID}\" (nome,cpf,desejo) VALUES ('{nome}', '{cpf}', '{desejo}');"
        )
        conn.commit()
        return jsonify(
            {
                "tableID": tableID,
                "nome": nome,
                "cpf": cpf,
                "desejo": desejo,
                "response": "200"
            }
        )

    except Exception as e:
        return jsonify(
            {
                "tableID": tableID,
                "nome": nome,
                "cpf": cpf,
                "desejo": desejo,
                "response": "100"
            }
        )

@app.route("/session/create/", methods=["POST"])
def createTable():
    requerimento = request.get_json()

    try:
        hostcpf = requerimento["cpf"]
        tableID = requerimento["tableID"]
        nome = requerimento["nome"]
        desejo = requerimento["desejo"]

        if func.invalidCpf(func.limpar_cpf(hostcpf)):
            return jsonify(
                {
                    "tableID": tableID,
                    "nome": nome,
                    "cpf": hostcpf,
                    "desejo": desejo,
                    "response": "cpf inválido!",
                }
            )

        key = func.gerarID()
        while True:
            cursor.execute(f"select id_table from hosts where id_table='{key}'")
            if cursor.fetchone() is None:
                break
            key = func.gerarID()

        cursor.execute(
            f"INSERT INTO hosts values('{func.limpar_cpf(hostcpf)}', '{key}')"
        )
        conn.commit()

        cursor.execute(
            f'CREATE TABLE "{key}"(id_guest serial not null,'
            + "nome varchar(25) not null,amigosecretoid int,cpf varchar(14),"
            + "desejo varchar(255),"
            + "primary key(id_guest))"
        )
        conn.commit()

       
        cursor.execute(
            f'insert into "{key}" (nome,cpf,desejo) values(\'{nome}\',\'{hostcpf}\',\'{desejo}\')'
        )
        conn.commit()



        return jsonify(
            {
                "tableID": key,
                "nome": nome,
                "cpf": hostcpf,
                "desejo": desejo,
                "response":"200",
            }
        )
    except Exception as e:
        return jsonify(
            {
                "tableID": tableID,
                "nome": nome,
                "cpf": hostcpf,
                "desejo": desejo,
                "response": f"Erro:{e}",
            }
        )

@app.route("/session/sortition/verify", methods=["POST"])
def verifySortition():
    requerimento = request.get_json()

    guestcpf = requerimento["cpf"]
    tableID = requerimento["tableID"]
    nome = requerimento["nome"]
    desejo = requerimento["desejo"]
 
    try:
        if(func.invalidCpf(guestcpf)):
            return jsonify(
                    {
                        "tableID": tableID,
                        "nome": nome,
                        "cpf": guestcpf,
                        "desejo": desejo,
                        "response": "001",
                    }
                )
        elif(not verificarTableID(tableID)):
            return jsonify(
                    {
                        "tableID": tableID,
                        "nome": nome,
                        "cpf": guestcpf,
                        "desejo": desejo,
                        "response": "002",
                    }
                )
        elif(not verifyGuest(guestcpf,tableID)):
            return jsonify(
                    {
                        "tableID": tableID,
                        "nome": nome,
                        "cpf": guestcpf,
                        "desejo": desejo,
                        "response": "003",
                    }
                )
        elif(sorteioAconteceu(tableID)):
            return jsonify(
                    {
                        "tableID": tableID,
                        "nome": nome,
                        "cpf": guestcpf,
                        "desejo": desejo,
                        "response": "004",
                    }
                )

        cursor.execute(
                    f"select nome from \"{tableID}\" where id_guest = (select amigosecretoid from \"{tableID}\" where cpf = '{guestcpf}')"
                )
        nome = cursor.fetchone()[0]
        
        cursor.execute(
                    f"select desejo from \"{tableID}\" where id_guest = (select amigosecretoid from \"{tableID}\" where cpf = '{guestcpf}')"
                )
        desejo = cursor.fetchone()[0]
        
        return jsonify(
                    {
                        "tableID": tableID,
                        "nome": nome,
                        "cpf": guestcpf,
                        "desejo": desejo,
                        "response": "200",
                    }
                )
    except:
        return jsonify(
                    {
                        "tableID": tableID,
                        "nome": nome,
                        "cpf": guestcpf,
                        "desejo": desejo,
                        "response": "004",
                    }
                )

@app.route("/session/requere/<string:cpf>", methods=["GET"])
def requerirsessoes(cpf):
    lista = []

    if(not func.invalidCpf(func.limpar_cpf(cpf))):
        if(verifyGuest(cpf,"hosts")):
            cursor.execute(f"select id_table from hosts where cpf = '{cpf}'")
            resposta = cursor.fetchall()
            resposta = func.matrizParray(resposta)
            listaTam = []

            for i in resposta:
                listaTam.append(contarparticipantes(i))

            return jsonify({
            "sessoes": resposta,
            "tamanho": listaTam,
            "response": "200"
            })
        return jsonify({
            "sessoes": lista,
            "tamanho": [],
            "response": "002"
            })        
    else:
        return jsonify({
            "sessoes": lista,
            "tamanho": [],
            "response": "001"
        })
#001-cpf/002-nHost

@app.route("/session/delete/<string:id>", methods=["DELETE"])
def deletarSessao(id):
    cursor.execute(f'drop table "{id}"')
    conn.commit()
    cursor.execute(f"DELETE FROM hosts WHERE id_table = '{id}'")
    conn.commit()

    return jsonify({})

@app.route("/session/sortition/start", methods=["POST"])
def sortear():
    requerimento = request.get_json()

    decisao = requerimento["decisao"]
    idsessao = requerimento["sessaoid"]

    if(not verificarTableID(idsessao)):
        return jsonify({
            "decisao": decisao,
            "sessaoid": idsessao,
            "response": False
        })
    elif(contarparticipantes(idsessao)<3):
        return jsonify({
            "decisao": decisao,
            "sessaoid": idsessao,
            "response": False
        })
    else:
        realizarSorteio(idsessao)
        return jsonify({
            "decisao": decisao,
            "sessaoid": idsessao,
            "response": True
        }) 
#001-Tableid/002-menorq3

def sorteioAconteceu(tableid=str()):
    if not verificarTableID(tableid):
        return False

    cursor.execute(
            f'SELECT EXISTS (SELECT 1 FROM "{tableid}" WHERE amigosecretoid IS NULL)'
        )

    return cursor.fetchone()[0]
    
def verifyGuest(cpf=str(), tableID=str()):
    tableID = f'"{tableID}"'

    cursor.execute(f"select cpf from {tableID} where cpf='{cpf}'")
    resultado = cursor.fetchone()[0]
    try:
        
        return True
    except:
        return False

def verificarTableID(tableID=str()):
    if func.invalidValue(tableID,10,10):
        return False
    cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{tableID}')")
    return cursor.fetchone()[0]

def realizarSorteio(tableID=str()):
    
    # Executando a consulta SQL
    cursor.execute(f'select id_guest from "{tableID}"')
    resultados = cursor.fetchall()

    lista_participantes = []

    # add na lista participante
    for i in resultados:
        lista_participantes.append(int(i[0]))


    lista_sorteio = func.processarSorteio(lista_participantes)

    for i in range(len(lista_sorteio)):
        cursor.execute(f'UPDATE "{tableID}" SET amigosecretoid = {lista_sorteio[i]} WHERE id_guest = {lista_participantes[i]};')
        conn.commit()
    
    return lista_sorteio   

def contarparticipantes(tableID=str()):
    cursor.execute(f'select count(id_guest) from "{tableID}"')
    return cursor.fetchone()[0]


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
