import os

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secretkey@@@###')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DB_URI = os.getenv('DB_URI', 'mongodb://localhost:27017/')

# Connessione a MongoDB
client = MongoClient(DB_URI)
db = client['api_gateway_db']
routes_collection = db['routes']

# Credenziali fisse (hardcoded)
USERNAME = os.getenv('USERNAME', 'admin')
PASSWORD = os.getenv('PASSWORD', 'password')


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    if username == USERNAME:
        return User(username)
    return None

@app.route('/login_admin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verifica delle credenziali fisse
        if username == USERNAME and password == PASSWORD:
            user = User(username)
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials, please try again.')

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Funzione per ottenere tutte le mappature
def get_all_routes():
    routes = {}
    for route in routes_collection.find():
        routes[route['endpoint']] = route['external_url']
    return routes


# Admin dashboard - Pagina principale
@app.route('/admin', methods=['GET'])
@login_required
def admin_dashboard():
    routes = get_all_routes()
    return render_template('admin_dashboard.html', routes=routes)


@app.route('/admin/add_route', methods=['POST'])
@login_required
def add_route():
    endpoint = request.form.get('endpoint')
    external_url = request.form.get('external_url')

    if not endpoint or not external_url:
        return jsonify({"error": "endpoint and external_url are required"}), 400

    # Controlla se l'endpoint esiste già nel database
    if routes_collection.find_one({'endpoint': endpoint}):
        return jsonify({"error": "Endpoint already exists"}), 400

    # Inserisci nel database
    routes_collection.insert_one({
        'endpoint': endpoint,
        'external_url': external_url
    })

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_route/<path:endpoint_name>', methods=['POST'])
@login_required
def delete_route(endpoint_name):
    routes_collection.delete_one({'endpoint': endpoint_name})
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/test_route', methods=['POST'])
def test_route():
    endpoint = request.form.get('endpoint')
    method = request.form.get('method')
    params = request.form.get('params')  # Parametri query come stringa
    body = request.form.get('body')  # Corpo JSON per POST/PUT
    headers = request.form.get('headers')  # Header JSON
    response_text = None
    status_code = None

    route = routes_collection.find_one({'endpoint': endpoint})

    if not route:
        return render_template('admin_dashboard.html', routes=get_all_routes(), error="Endpoint not found")

    external_url = route['external_url']

    # Se ci sono parametri query, aggiungili all'URL
    if params:
        external_url += '?' + params

    # Converte il corpo in JSON se presente
    json_body = None
    if body:
        try:
            json_body = json.loads(body)
        except ValueError:
            return render_template('admin_dashboard.html', routes=get_all_routes(), error="Invalid JSON body")

    headers_dict = {}
    if headers:
        try:
            headers_dict = json.loads(headers)
        except ValueError:
            return render_template('admin_dashboard.html', routes=get_all_routes(), error="Invalid Headers JSON")

    try:
        # Inoltra la richiesta all'URL esterno
        response = requests.request(method, external_url, json=json_body, headers=headers_dict)

        # Raccogli la risposta dall'URL esterno
        status_code = response.status_code
        if response.headers.get('Content-Type') == 'application/json':
            response_text = response.json()
        else:
            response_text = response.text

    except Exception as e:
        return render_template('admin_dashboard.html', routes=get_all_routes(), error=f"Error: {str(e)}")

    # Passa la risposta al template per visualizzarla
    return render_template('admin_dashboard.html', routes=get_all_routes(), response=response_text,
                           status_code=status_code)


@app.route('/admin/edit_route/<path:endpoint_name>', methods=['GET', 'POST'])
@login_required
def edit_route(endpoint_name):
    routes = get_all_routes()
    if request.method == 'POST':
        new_endpoint = request.form.get('new_endpoint')
        new_external_url = request.form.get('new_external_url')

        # Verifica se l'endpoint modificato esiste già
        if not new_endpoint or not new_external_url:
            return "Error: endpoint and external_url are required", 400

        # Se l'endpoint è cambiato, dobbiamo eliminare il vecchio e aggiungere il nuovo
        routes_collection.delete_one({'endpoint': endpoint_name})

        # Forza il delete
        routes_collection.delete_one({'endpoint': new_endpoint})

        # Aggiungi o aggiorna l'endpoint nel dizionario
        routes_collection.insert_one({
            'endpoint': new_endpoint,
            'external_url': new_external_url
        })

        return redirect(url_for('admin_dashboard'))

    return render_template('edit_route.html', endpoint_name=endpoint_name, external_url=routes[endpoint_name])


@app.route('/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(endpoint):
    route = routes_collection.find_one({'endpoint': endpoint})
    if not route:
        return jsonify({"error": "Endpoint not found"}), 404

    external_url = route['external_url']

    params = request.args.to_dict()
    method = request.method
    headers = dict(request.headers)
    data = request.get_json() if 'GET' not in method else None

    try:
        # Fai la richiesta all'URL esterno con lo stesso metodo e dati
        response = requests.request(method, external_url, headers=headers, json=data, params=params)

        # Restituisci la risposta dall'URL esterno
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json(), response.status_code, response.headers.items()
        elif 'text/html' in content_type:
            return response.text, response.status_code, response.headers.items()
        else:
            return response.content, response.status_code, response.headers.items()

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
