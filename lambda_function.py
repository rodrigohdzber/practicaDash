import json
import pandas as pd
import requests
import pymysql
import datetime
import sqlalchemy as db

def lambda_handler(event, context):
    hoy = datetime.datetime.today().strftime('%Y-%m-%d')
    
    url2 = "https://api.esios.ree.es/archives/70/download_json?locale=es&date=" + hoy
    
    response = requests.get(url2)
    df2 = pd.DataFrame(response.json()["PVPC"])
    #df["fecha"] = datetime.datetime(df["Dia"]+df["Hora"])
    lista2 = list(df2["PCB"])

    nueva_PCB2 = [c.replace(',', '.') for c in lista2]
    
    l2 = [float(i) for i in nueva_PCB2]

    lista_dias2 = df2["Hora"]
    
    k2 = [i[0:2] for i in lista_dias2]

    lista_fechas = list(df2["Dia"])
    nueva_fecha = [datetime.datetime.strptime(fecha,'%d/%m/%Y') for fecha in lista_fechas]
    df2["Dia"] = nueva_fecha
    df2["valor"] = l2
    df2["hora"] = k2
    df2["fecha"] = df2["Dia"]
    df2 = df2[['fecha','hora', 'valor']]
    print(df2)

    tipo = "mysql+pymysql"
    user = "admin"
    password = "adminadmin"
    host = "database-2.cwtwnmjvvlr5.eu-west-3.rds.amazonaws.com"
    bbdd = "ECI"

    #Conectamos a BBDD
    path = tipo + "://" + user + ":" + password + "@" + host + "/" + bbdd
    engine = db.create_engine(path)
    con = engine.connect()

    #creas el df
    df2.to_sql("Pvpc", con, if_exists = 'append', index=False)
    # TODO implement
    #return df2
    #return json.loads(json.dumps(df2, default=str))
    return ""