import pandas as pd
import dash
from dash import dcc   #para los graficos.
from dash import html  #para poner h1, div como hicimos al crear la pagina web
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import requests
from datetime import date
import pymysql
import datetime
import sqlalchemy as db

#DE MOMENTO EL FICHERO RUN NO VALE PARA NADA.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets) #creas un objeto que se llama app
#aquí estamos creando la web por decirlo así estaría vacía. y los estilos
#y luego tendrá distintas propiedades como layout que es para ir rellenando la web igual que haciamos en html

today = datetime.datetime.today().strftime('%Y-%m-%d')
fecha1 = datetime.datetime.today()
fecha2 = fecha1 - timedelta(days=30)
fecha1 = fecha1.strftime('%Y-%m-%d')
fecha2 = fecha2.strftime('%Y-%m-%d')

def esios(fecha): #esta coge los datos de la api

    hoy = datetime.datetime.today().strftime('%Y-%m-%d')
    url = "https://api.esios.ree.es/archives/70/download_json?locale=es&date=" + fecha
    url2 = "https://api.esios.ree.es/archives/70/download_json?locale=es&date=" + hoy


    response = requests.get(url)
    df = pd.DataFrame(response.json()["PVPC"])

    response = requests.get(url2)
    df2 = pd.DataFrame(response.json()["PVPC"])
    #df["fecha"] = datetime.datetime(df["Dia"]+df["Hora"])
    lista = list(df["PCB"])
    lista2 = list(df2["PCB"])

    nueva_PCB = [c.replace(',', '.') for c in lista]
    nueva_PCB2 = [c.replace(',', '.') for c in lista2]
    l = [float(i) for i in nueva_PCB]
    l2 = [float(i) for i in nueva_PCB2]

    lista_dias = df["Hora"]
    lista_dias2 = df2["Hora"]
    k = [i[0:2] for i in lista_dias]
    k2 = [i[0:2] for i in lista_dias2]

    df["PCB"] = l
    df["Hora"] = k
    df = df[['Dia','Hora', 'PCB']]

    df2["PCB"] = l2
    df2["Hora"] = k2
    df2 = df2[['Dia','Hora', 'PCB']]

    df_final = pd.concat([df, df2])

    #df['PCB_today'] = df2['PCB']
    #print(df_final)

    return df_final

def esios_bd(fecha):  #esta es la nueva que he creado cogiendo los datos de nuestra bd.
    hoy = datetime.datetime.today().strftime('%Y-%m-%d')
    tipo = "mysql+pymysql"
    user = "admin"
    password = "adminadmin"
    host = "database-2.cwtwnmjvvlr5.eu-west-3.rds.amazonaws.com"
    bbdd = "ECI"
    hoy = datetime.datetime.today().strftime('%Y-%m-%d')
    #Conectamos a BBDD
    path = tipo + "://" + user + ":" + password + "@" + host + "/" + bbdd
    engine = db.create_engine(path)
    con = engine.connect()
    #hoy = str(hoy)
    query = "SELECT fecha, hora, valor FROM Pvpc WHERE fecha =" + f"'{hoy}'"  + ";"
    tabla = con.execute(query)
    df = pd.DataFrame(tabla)
    #print(df)
    query2 = "SELECT fecha, hora, valor FROM Pvpc WHERE fecha =" + f"'{fecha}'"  + ";"
    tabla2 = con.execute(query2)
    df2 = pd.DataFrame(tabla2)
    #print(df2)
    df_final = pd.concat([df,df2])
    df_final.columns = ["fecha", "hora", "valor"]

    return df_final

def historico(fecha1, fecha2):  #esta es la nueva que he creado cogiendo los datos de nuestra bd.
    #hoy = datetime.datetime.today().strftime('%Y-%m-%d')
    #fecha1 = datetime.datetime.today()
    #fecha2 = fecha1 - timedelta(days=30)
    #fecha1 = fecha1.strftime('%Y-%m-%d')
    #fecha2 = fecha2.strftime('%Y-%m-%d')
    print(fecha1)
    print(fecha2)
    tipo = "mysql+pymysql"
    user = "admin"
    password = "adminadmin"
    host = "database-2.cwtwnmjvvlr5.eu-west-3.rds.amazonaws.com"
    bbdd = "ECI"
    hoy = datetime.datetime.today().strftime('%Y-%m-%d')
    #Conectamos a BBDD
    path = tipo + "://" + user + ":" + password + "@" + host + "/" + bbdd
    engine = db.create_engine(path)
    con = engine.connect()
    #hoy = str(hoy)
    query = "SELECT fecha, hora, valor FROM Pvpc WHERE fecha BETWEEN " + f"'{fecha2}'" + "AND" + f"'{fecha1}'"  + ";"
    tabla = con.execute(query)
    df = pd.DataFrame(tabla)
    print(df)
    df.columns = ["fecha", "hora", "valor"]
    df = df[['fecha', 'valor']]
    #print(df.info())
    df['valor'] = df['valor'].apply(pd.to_numeric, errors='coerce')
    df = df.groupby(['fecha']).mean()
    #print(df)
    df = df.reset_index()
    #df.columns = ["fecha", "hora", "valor"]
    #print(df)

    return df


#df.index = df["Hora"]

datos = esios_bd(today)

fig = px.line(datos, x=datos['hora'], y=datos['valor'])

datos2 = historico(fecha1, fecha2)

fig2 = px.line(datos2, x=datos2['fecha'], y=datos2['valor'])



app.layout = html.Div(children=[  #PONEMOS LOS ATRIBUTOS A LA APP(WEB) UN TITULO, UN SEGUNDO TITULO, Y UN GRAFICO.
    html.H1(
        children='PVPC del día ' + today,
    ),
    html.H5(
        children='mIAx Práctica modulo 3',
    ),
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=date(2016, 1, 1),
        max_date_allowed=date(2021, 12, 31),
        initial_visible_month=date(2021, 12, 1),
        date=date(2021, 12, 1),
        display_format='Y-M-D'
    ),
    html.Div(id='select_day'),

    dcc.Graph(
        id='graph',
        #figure=fig aqui ya no hace falta está puesto abajo
    ),
    html.H6(
        children='Precio historico',
    ),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2016, 12, 1),
        max_date_allowed=date(2021, 12, 31),
        initial_visible_month=date(2021, 11, 1),
        start_date=date(2021, 11, 1),
        end_date=date(2021, 12, 1)
    ),
    html.Div(id='output-container-date-picker-range'),

    dcc.Graph(
        id='graph2',
        #figure=fig aqui ya no hace falta está puesto abajo
    )
])

@app.callback(
    Output('select_day', 'options'),
    Input('my-date-picker-single', 'date'))
def update_output(date_value):
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%Y-%m-%d')
        return date_string

@app.callback( 
    Output("graph", "figure"),
    Input("select_day", "options"))
def change_graph(fecha):  
    data = esios_bd(fecha)
    data['fecha'] = data['fecha'].astype('str')
    #print(data.info())
    fig = px.line(data,
        x = data['hora'],
        y= data['valor'],
        color=data['fecha']
    )  
    return fig

@app.callback(
    Output('output-container-date-picker-range', 'options'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output2(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        lista = [start_date_string, end_date_string]
        return lista

@app.callback( 
    Output("graph2", "figure"),
    Input('output-container-date-picker-range', 'options'))
    #Input("output-container-date-picker-range", "options")
def change_graph2(options):
    start_date = options[1]
    end_date = options[0]
    print(start_date)
    print(end_date)
    data2 = historico(start_date, end_date)
    data2['fecha'] = data2['fecha'].astype('str')
    print(data2)
    fig2 = px.line(data2,
        x = data2['fecha'],
        y= data2['valor']
        )  
    return fig2   

if __name__ == "__main__":  #ejecuta la aplicacion..
    app.run_server(host="127.0.0.1", debug=False, port=8050)  #QUE CORRA LA APLICACION DE ARRIBA.
   #app.run_server(host="0.0.0.0", debug=False, port=8080)