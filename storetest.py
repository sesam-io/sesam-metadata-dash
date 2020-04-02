import dash
import pandas as pd

from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

import dash_html_components as html
import dash_core_components as dcc
import dash_table

import keyring
import requests
import json

password = keyring.get_password("morten-dev","mof")
hubNr = "8a651472"
apiurl = f"https://datahub-{hubNr}.sesam.cloud/api/"
header = {'Authorization': 'Bearer ' + password,'Content-type': "application/json"}

def getPipesData():
    url_pipes = apiurl+f"pipes"
    resp_pipes = requests.get(url_pipes,headers=header)
    return pd.json_normalize(resp_pipes.json())

app = dash.Dash(__name__)

df = getPipesData()
columnNames = set(df.columns)

app.layout = html.Div([
    dcc.Store(id='memory-output'),
    dcc.Dropdown(id='memory-pipes', options=[
        {'value': x, 'label': x} for x in columnNames
    ], multi=True, value=['_id', 'storage']),
    html.Div(id='memory-table')
])

@app.callback(Output('memory-output', 'data'),
              [Input('memory-pipes', 'value')])
def filter_pipes(columnNames_selected):
    if not columnNames_selected:
        # Return all the rows on initial load/no country selected.
        return df.to_dict('records')
    filtered = df[columnNames_selected] #df.query('country in @columnNames_selected')
    return filtered.to_dict('records')

@app.callback(Output('memory-table', 'children'),
              [Input('memory-output', 'data')])
def on_data_set_table(data):
    if data is None:
        raise PreventUpdate
    return html.Div([dash_table.DataTable(style_table={'maxHeight': '300px','overflowY': 'scroll'},
            id='table',
            columns=[{'name': i, 'id': i} for i in list(data[0].keys())],
            data=data
        )])

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True, port=10450)
