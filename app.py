import sys
import json

from MDAPy import MDAPy_Functions as mda
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin


app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def index():
    print(mda.__dir__())
    return jsonify('MDAPy API home')

@app.route('/validate', methods=['POST'])
@cross_origin()
def check_validity():
    data = json.loads(request.data)
    # for now only return params
    return jsonify(data)

