import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table

import plotly.graph_objects as go

from dash.dependencies import Input, Output

import keyring
import requests
import pandas
import json

password = keyring.get_password("morten-dev","mof")
hubNr = "8a651472"
apiurl = f"https://datahub-{hubNr}.sesam.cloud/api/"
header = {'Authorization': 'Bearer ' + password,'Content-type': "application/json"}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def getNodeInfo():
    resp_api = requests.get(apiurl)
    return resp_api.json()

def getSystemsData():
    url_systems = apiurl+f"systems"
    resp_systems = requests.get(url_systems,headers=header)
    return pandas.json_normalize(resp_systems.json())

def getPipesData():
    url_pipes = apiurl+f"pipes"
    resp_pipes = requests.get(url_pipes,headers=header)
    return pandas.json_normalize(resp_pipes.json())

def getEntities(pipeId):
    url_entities = apiurl+f"pipes/{pipeId}/entities?limit=10"
    resp_entities = requests.get(url_entities,headers=header)
    return pandas.json_normalize(resp_entities.json())

def generateTable(df):
    return dash_table.DataTable(style_table={'maxHeight': '300px','overflowY': 'scroll'},
                    style_cell={'textAlign': 'left'},
                    id='table',
                    columns=[{"name": f'{i} ({j})', "id": i} for i,j in zip(df.columns, df.dtypes)],
                    data=df.to_dict('records'))

app.layout = html.Div([
    dcc.Tabs(id="tabs", value='node', children=[
        dcc.Tab(label='Node info', value='node'),
        dcc.Tab(label='Systems', value='systems'),
        dcc.Tab(label='Pipes', value='pipes'),
        dcc.Tab(label='Entities', value='entities')
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'),[Input('tabs', 'value')])
def render_content(tab):
    data = list()
    if tab == "node":
        node_data = getNodeInfo()
        return html.Div([
            html.Pre(json.dumps(node_data,indent=4))
                        ])
    if tab == "systems":
        systems_data = getSystemsData()
        systems_count = systems_data.groupby("config.effective.type")['_id'].count()
        data = [{'labels': list(systems_count.index),'values': list(systems_count),'type': 'pie'}]
        return html.Div([
            dcc.Graph(id='graph',figure={'data': data,'layout': {'margin': {'l': 30,'r': 0,'b': 30,'t': 30}}}),
            generateTable(systems_data)
                        ])
    if tab == "pipes":
        pipes_data = getPipesData()
        pipes_count = pipes_data.groupby("config.original.source.type")._id.count()
        data = [{'labels': list(pipes_count.index),'values': list(pipes_count),'type': 'pie'}]
        return html.Div([
            dcc.Graph(id='graph',figure={'data': data,'layout': {'margin': {'l': 30,'r': 0,'b': 30,'t': 30}}}),
            generateTable(pipes_data[pipes_data.columns.to_list()[0:6]])
            ])
    if tab == "entities":
        node_entities = getEntities("test-rest-brreg-naeringskode")
        return html.Div([
            generateTable(pandas.DataFrame(node_entities))
                        ])

if __name__ == '__main__':
    app.run_server(debug=True,dev_tools_ui=True)