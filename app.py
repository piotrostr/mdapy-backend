import sys
import json

from mdapy import load_data, validate_analyses_df
from MDAPy import MDAPy_Functions as mdapy
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

def get_allowed():
    methods_allowed = 'GET,HEAD,OPTIONS,POST,PUT'
    headers_allowed = 'Access-Control-Allow-Headers, Origin, Accept, ' 
    headers_allowed += 'X-Requested-With, Content-Type, ' 
    headers_allowed += 'Access-Control-Request-Method, ' 
    headers_allowed += 'Access-Control-Request-Headers'
    return headers_allowed, methods_allowed

@app.route('/')
def index():
    print(mda.__dir__())
    return jsonify('MDAPy API home')

@app.route('/validate', methods=['POST', 'OPTIONS'])
def check_validity():
    if len(request.data):
        data = json.loads(request.data)
        column_names = data['table']['columnLabels']
        dataset = data['dataset']
        arrays = data['table']['data']
        arrays = [[i['value'] for i in row] for row in arrays]
        if dataset == 'Best Age and sx':
            data_type = 'Ages'
        elif dataset == 'U-Pb 238/206 & Pb-Pb 207/206':
            data_type = '238U/206Pb_&_207Pb/206Pb'
        *_, analyses_df = load_data(arrays, column_names, data_type)
        sample_amounts_table = validate_analyses_df(analyses_df, data_type)
        response = make_response(sample_amounts_table.to_json())
    else:
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
    headers_allowed, methods_allowed = get_allowed()
    response.headers['Access-Control-Allow-Origin'] = '*' 
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = methods_allowed
    response.headers['Access-Control-Allow-Headers'] = headers_allowed
    response.headers['Content-Type'] = 'application/json'
    return response
