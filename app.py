import sys
import json

from mdapy import load_data, validate_analyses_df
from MDAPy import MDAPy_Functions as mdapy
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

@app.route('/')
def index():
    print(mda.__dir__())
    return jsonify('MDAPy API home')

@app.route('/validate', methods=['POST', 'OPTIONS'])
def check_validity():
    if len(request.data):
        data = json.loads(request.data)
        # *_, analyses_df = load_data(data['table'])
        response = make_response(data)
    else:
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
    methods_allowed = 'GET,HEAD,OPTIONS,POST,PUT'
    headers_allowed = 'Access-Control-Allow-Headers, Origin, Accept, ' 
    headers_allowed += 'X-Requested-With, Content-Type, ' 
    headers_allowed += 'Access-Control-Request-Method, ' 
    headers_allowed += 'Access-Control-Request-Headers'
    response.headers['Access-Control-Allow-Origin'] = '*' 
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = methods_allowed
    response.headers['Access-Control-Allow-Headers'] = headers_allowed
    response.headers['Content-Type'] = 'application/json'
    return response
