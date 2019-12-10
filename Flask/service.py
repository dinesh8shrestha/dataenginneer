#
# Simple Flask app
#
from string import ascii_letters, digits

from urllib.request import urlopen
from urllib.parse import quote

import requests

from flask import Flask
from flask import request, abort, jsonify, make_response #, send_from_directory

#Clickhouse address.
# if called from a container - should be external
# otherwise can be localhost or an internal address
host = "localhost"
clickhouse_port = 8123 # REST API

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Welcome to online stats!'

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/get_most_recent_stats_params', methods=['GET'])
def get_most_recent_stats_params():
    fields = request.args.get('fields')
    table = request.args.get('table')

    #validate input to avoid sql injection attacks
    valid_fields = all(c in valid_symbols_and_sep for c in fields)
    valid_table  = all(c in valid_symbols for c in table)
    if not valid_fields or not valid_table:
       error = 'valid symbols for fields and table are '+ valid_symbols_and_sep
       return make_response(jsonify({'error': error}), 400)
    
    query = "SELECT {} from {}".format(fields, table)
    url = 'http://{}:{}/?query={}'.format(host, clickhouse_port, quote(query))
    response = requests.get(url)
    if response.status_code  == 200:
       #parse output
       out = {f:v for f,v in zip(fields.split(','), response.text.strip().split('\t'))}
       return make_response(jsonify(out), response.status_code)
    else:
       return make_response(jsonify({'error': response.text}), response.status_code)




if __name__ == '__main__':
    valid_symbols = ascii_letters+digits+'_.'
    valid_symbols_and_sep = valid_symbols + ","


    app.run(debug=True, host='0.0.0.0')
    
