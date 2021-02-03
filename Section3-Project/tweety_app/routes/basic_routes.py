from flask import Blueprint, render_template, jsonify, request
from tweety_app.models import Users, parse_records, get_all_data
from tweety_app.tweety_api import api

basic_routes = Blueprint('basic_routes', __name__)

# '/'
@basic_routes.route('/')
def index():
    return render_template("index.html")

# '/add.json
@basic_routes.route('/add.json')
def json_data():
    raw_data = get_all_data()
    parsed_data = parse_records(raw_data)
    
    return jsonify(parsed_data)

@basic_routes.route('/users', methods=["GET", "POST"])
def users():
    data = get_all_data()
    description = ''
    return render_template('users.html', description=description, data=data)
    