from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import configparser
import os

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, '../config.ini')

config = configparser.ConfigParser(interpolation=None)
config.read(config_file_path)

def get_db_connection():

    # db connection access params
    conn_params = {
        'dbname': config['database']['dbname'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'host': config['database']['host'],
        'port': config['database']['port']
    }
    
    conn = psycopg2.connect(**conn_params)
    
    return conn

@app.route('/api/locations', methods=['GET'])
def get_locations():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT case_number, county, start_date, parcel_id, property_address, appraised_value, opening_bid, deposit_requirement, lat, lon FROM auction_items')
    locations = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(locations)

if __name__ == '__main__':
    app.run(debug=True)