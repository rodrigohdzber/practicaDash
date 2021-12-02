import pandas as pd
import dash
from dash import dcc   #para los graficos.
from dash import html  #para poner h1, div como hicimos al crear la pagina web
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import requests
from datetime import date

#DE MOMENTO EL FICHERO RUN NO VALE PARA NADA.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets) #creas un objeto que se llama app
#aquí estamos creando la web por decirlo así estaría vacía. y los estilos
#y luego tendrá distintas propiedades como layout que es para ir rellenando la web igual que haciamos en html

today = datetime.today().strftime('%Y-%m-%d')

def esios(fecha):

    hoy = datetime.today().strftime('%Y-%m-%d')
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
    print(df_final)

    return df_final



#df.index = df["Hora"]

datos = esios(today)

fig = px.line(datos, x=datos['Hora'], y=datos['PCB'], color='Dia')



app.layout = html.Div(children=[  #PONEMOS LOS ATRIBUTOS A LA APP(WEB) UN TITULO, UN SEGUNDO TITULO, Y UN GRAFICO.
    html.H1(
        children='PVPC del día ' + today,
    ),
    html.H5(
        children='mIAx Práctica modulo 3',
    ),
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=date(2021, 6, 1),
        max_date_allowed=date(2021, 11, 24),
        initial_visible_month=date(2021, 8, 5),
        date=date(2021, 8, 25),
        display_format='Y-M-D'
    ),
    html.Div(id='select_day'),

    dcc.Graph(
        id='graph',
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
    data = esios(fecha)
    fig = px.line(data,
        x = data['Hora'],
        y= data['PCB'],
        color=data['Dia']
    )  
    return fig

if __name__ == "__main__":  #ejecuta la aplicacion.
    app.run_server(host="0.0.0.0", debug=False, port=8080)  #QUE CORRA LA APLICACION DE ARRIBA.
