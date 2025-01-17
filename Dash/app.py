import dash
from dash import dcc, html,dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime as dt
import base64
import plotly.express as px
import geopandas as gpd
from sklearn.preprocessing import robust_scale
from sklearn.cluster import KMeans



app = dash.Dash(__name__)

with open('../data/cultivos.csv', 'r', encoding='utf-8') as file:
    Inputs = pd.read_csv(file)


grupos_cultivos = Inputs['GRUPO_CULTIVO'].unique().tolist()
años = Inputs['ANIO'].unique().tolist()
departamentos = Inputs['NOMBRE_DEPARTAMENTO'].unique().tolist()
cultivos = Inputs['NOMBRE_CULTIVO'].unique().tolist()

CantidadCultivos = len(Inputs['NOMBRE_CULTIVO'].unique())

#AreaSembrada = Inputs["Área Sembrada(ha)"].sum()
#AreaCosechada = Inputs["Área Cosechada(ha)"].sum()

# Datos de ejemplo

df = pd.DataFrame(Inputs, columns=[ 'NOMBRE_DEPARTAMENTO', 'NOMBRE_MUNICIPIO','GRUPO_CULTIVO', 'NOMBRE_CULTIVO', 'RENDIMIENTO_TONELADAS_HA']).head(10)
                                                                                                                
with open('./img/Logo.png', 'rb') as f:
    logo_data = f.read()
encoded_logo = base64.b64encode(logo_data).decode()

app.layout = html.Div([
# Contenedor header
html.Div([
    html.Img(src=f"data:image/png;base64,{encoded_logo}", height=100),
    html.H1("Rendimiento Agrícola por Hectárea"),
], className="header"),

#contenedor de los dropdowns o filtros
html.Div([
# Contenedor fILTROS
html.Div([
html.H6("Departamento"),
dcc.Dropdown(
id="dropdown-departamento",
options=[{'label': departamento, 'value': departamento} for departamento in departamentos],
value=departamentos[0],
searchable=True  # Habilitar la opción de búsqueda
),
html.H6("Municipio"),
dcc.Dropdown(
id="dropdown-municipio",
# Aquí dejamos las opciones vacías por ahora, se llenarán con la actualización
options=[],
value=None,
searchable=True  # Habilitar la opción de búsqueda
),
html.H6("Año"),
dcc.Dropdown(
id="dropdown-año",
options=[{'label': str(año), 'value': año} for año in años],
value=años[0],
searchable=True  # Habilitar la opción de búsqueda
),
html.H6("Grupo de Cultivo"),
dcc.Dropdown(
id="dropdown-grupo-cultivo",
options=[{'label': grupo, 'value': grupo} for grupo in grupos_cultivos],
value=grupos_cultivos[0],
searchable=True  # Habilitar la opción de búsqueda
),
html.H6("Cultivo"),
dcc.Dropdown(
id="dropdown-cultivo",
options=[{'label': cultivo, 'value': cultivo} for cultivo in cultivos],
value=cultivos[0],
searchable=True  # Habilitar la opción de búsqueda
),

html.Button("Enviar Consulta",
id="enviar-button",
n_clicks=0,
style={'color': 'white'}
)

], className="left-container"),  # Contenedor izquierdo

html.Div([
html.Div([             
# Contenedor cards            

html.Div([             
    # Contenedor cards
    html.Div([                  
        html.Div("Cantidad de Cultivos", className="card-title"),
        html.Div(f"{CantidadCultivos}", className="card-valor", 
                 style={'backgroundColor': 'rgba(0,0,0,0)', 'color': '#2cfec1', 'textAlign': 'center','fontSize': '30px'}
                 ),
    ], className="card"),           

    html.Div([
        html.Div("Área Sembrada", className="card-titdle"),
        html.Div(f"{CantidadCultivos}", className="card-valor", 
                 style={'backgroundColor': 'rgba(0,0,0,0)', 'color': '#2cfec1', 'textAlign': 'center','fontSize': '30px'}
                 ),
    ], className="card"),

    html.Div([
        html.Div("Área Cosechada", className="card-title"),
        html.Div(f"{CantidadCultivos}", className="card-valor", 
                 style={'backgroundColor': 'rgba(0,0,0,0)', 'color': '#2cfec1', 'textAlign': 'center','fontSize': '30px'}
                 ),
    ], className="card"),# Contenedor cards
    # Contenedor de la tabla
    html.Div([
        html.H4('Tabla de Recomendaciones', className="title-visualizacion"),
        dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
                             style_cell={'backgroundColor': 'rgba(0,0,0,0)', 'color': '#2cfec1','textAlign': 'center'},
                             ), 
    ], className="table-container"),  # Contenedor de la tabla
], className="cards-container"), # Contenedor de las cards y la tabla

# Contenedor de la visualización del mapa
html.Div([
    html.H4('Grupo de Cultivos con Municipicos Similares', className="title-visualizacion"),
    dcc.RadioItems(
            id='candidate',
            options=["Joly", "Coderre", "Bergeron"],
            value="Coderre",
            inline=True
        ),
    dcc.Graph(id="mapa", className="mapa-graph",
              style={'backgroundColor': 'rgba(0,0,0,0)'}
              ), 
 
],className="mapa-container"),
# Contenedor de la tabla

html.Div([
html.H4('Rendimiento en Toneladas por Hectarea', className="title-visualizacion"),
dcc.Graph(id="line-chart", className="line-chart"),
], className="line-chart-container"),


], className="cards-container"), # Contenedor de las cards y la tabla
], className="main-container"),  # Contenedor derecho
#contenedor de las cards y la tabla


# Contenedor de la visualización del mapa

], className="main-container")
# Contenedor de la visualización de la gráfica de líneas  

])


#Llamado a la base de datosropdown municipio
@app.callback(
    Output("dropdown-municipio", "options"),
    [Input("dropdown-departamento", "value")]
)
def update_municipios(departamento):
    # Filtra los municipios basados en el departamento seleccionado
    municipios = Inputs[Inputs['NOMBRE_DEPARTAMENTO'] == departamento]['NOMBRE_MUNICIPIO'].unique()
    options = [{'label': municipio, 'value': municipio} for municipio in municipios]
    return options


#Llamado a la base de card 1

#llamado a la base de tabla


##mapa #https://plotly.com/python/maps/

@app.callback(
    Output("mapa", "figure"), 
    Input("candidate", "value"))


def display_choropleth(candidate):
    df = px.data.election() # replace with your own data source
    geojson = px.data.election_geojson()
    map = px.choropleth(
        df, geojson=geojson, color=candidate,
        locations="district", featureidkey="properties.district",
        projection="mercator", range_color=[0, 6500])
    map.update_geos(fitbounds="locations", visible=False)
    map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    map.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#2cfec1")
    return map 



##line chart
@app.callback(
    Output("line-chart", "figure"),
    [Input("dropdown-grupo-cultivo", "value"),
     Input("dropdown-año", "value"),
     Input("dropdown-municipio", "value"),
     Input("dropdown-departamento", "value"),
     Input("dropdown-cultivo", "value")]
)


#
def update_line_chart(grupo_cultivo, año, municipio, departamento, cultivo):
    # Filtra los datos basados en las selecciones
    filtered_data = Inputs[
        (Inputs['GRUPO_CULTIVO'] == grupo_cultivo) &
        (Inputs['ANIO'] == año) &
        (Inputs['NOMBRE_DEPARTAMENTO'] == departamento) &
        (Inputs['NOMBRE_MUNICIPIO'] == municipio) &
        (Inputs['NOMBRE_CULTIVO'] == cultivo)
    ]
    x_values = [1, 2, 3, 4, 5]
    y_values = [10, 8, 12, 6, 9]
    #x_values = filtered_data['FECHA']  # Reemplaza 'FECHA' con tu columna de fechas
    #y_values = filtered_data['RENDIMIENTO_TONELADAS_HA']  # Reemplaza con tus rendimientos

    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode='lines', marker_color='#2cfec1'))
    #fig = px.line(data2, x='local_timestamp', y="Demanda total [MW]", markers=True, labels={"local_timestamp": "Fecha"})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)', 
                      font_color="#2cfec1",
                      font_size=14,
                      xaxis_title="Fecha",
                      yaxis_title="Predición de Cultivo")
    fig.update_xaxes(showgrid=True, gridwidth=0.25, gridcolor='#7C7C7C')
    fig.update_yaxes(showgrid=True, gridwidth=0.25, gridcolor='#7C7C7C')
    #fig.update_traces(line_color='#2cfec1')

    return fig
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)
