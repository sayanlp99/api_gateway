import os
import requests
from flask import Flask, request, jsonify
from functools import wraps
import jwt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load environment variables
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL')
BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL')
EXCHANGE_SERVICE_URL = os.getenv('EXCHANGE_SERVICE_URL')
JWT_SECRET = os.getenv('JWT_SECRET')

# JWT Verification decorator
def verify_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"message": "Unauthorized: No token provided"}), 401

        try:
            # Decode JWT token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = decoded  # Save decoded user info to request
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 403

        return f(*args, **kwargs)
    return decorated_function

# Routes for Auth Service
@app.route('/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def auth_service(path):
    url = f"{AUTH_SERVICE_URL}/{path}"
    response = requests.request(method=request.method, url=url, json=request.get_json(), headers=request.headers)
    return jsonify(response.json()), response.status_code

# Routes for Book Service (protected)
@app.route('/books/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@verify_jwt
def book_service(path):
    url = f"{BOOK_SERVICE_URL}/{path}"
    response = requests.request(method=request.method, url=url, json=request.get_json(), headers=request.headers)
    return jsonify(response.json()), response.status_code

@app.route('/books', methods=['GET', 'POST'])
@verify_jwt
def book_service_root():
    url = f"{BOOK_SERVICE_URL}"
    response = requests.request(method=request.method, url=url, json=request.get_json(), headers=request.headers)
    return jsonify(response.json()), response.status_code

# Routes for Exchange Service (protected)
@app.route('/exchange/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@verify_jwt
def exchange_service(path):
    url = f"{EXCHANGE_SERVICE_URL}/{path}"
    response = requests.request(method=request.method, url=url, json=request.get_json(), headers=request.headers)
    return jsonify(response.json()), response.status_code

@app.route('/exchange', methods=['GET', 'POST'])
@verify_jwt
def exchange_service_root():
    url = f"{EXCHANGE_SERVICE_URL}"
    response = requests.request(method=request.method, url=url, json=request.get_json(), headers=request.headers)
    return jsonify(response.json()), response.status_code

# Start the Flask app
if __name__ == '__main__':
    app.run(port=int(os.getenv('FLASK_RUN_PORT', 3000)))
