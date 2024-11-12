import os
import requests
from flask import Flask, request, jsonify
from flask_restx import Api, Resource 
from functools import wraps
import jwt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
api = Api(app, doc='/docs', title="Booktrade API Gateway", description="API Gateway for Auth, Book, and Exchange Services")

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
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = decoded  # Save decoded user info to request
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 403

        return f(*args, **kwargs)
    return decorated_function

# Namespaces for organization
auth_ns = api.namespace('auth', description='Authentication Service')
books_ns = api.namespace('books', description='Book CRUD Service')
exchange_ns = api.namespace('exchange', description='Exchange Request Service')

# Routes for Auth Service
@auth_ns.route('/<path:path>')
class AuthService(Resource):
    def get(self, path):
        """Forward GET requests to the Auth Service"""
        url = f"{AUTH_SERVICE_URL}/{path}"
        response = requests.get(url, headers=request.headers)
        return response.json(), response.status_code

    def post(self, path):
        """Forward POST requests to the Auth Service"""
        url = f"{AUTH_SERVICE_URL}/{path}"
        response = requests.post(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code

# Routes for Book Service (protected)
@books_ns.route('/<path:path>')
class BookService(Resource):
    @verify_jwt
    def get(self, path):
        """Forward GET requests to the Book Service (JWT protected)"""
        url = f"{BOOK_SERVICE_URL}/{path}"
        response = requests.get(url, headers=request.headers)
        return response.json(), response.status_code

    @verify_jwt
    def post(self, path):
        """Forward POST requests to the Book Service (JWT protected)"""
        url = f"{BOOK_SERVICE_URL}/{path}"
        response = requests.post(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code

@books_ns.route('/')
class BookServiceRoot(Resource):
    @verify_jwt
    def get(self):
        """Get all books (JWT protected)"""
        url = f"{BOOK_SERVICE_URL}"
        response = requests.get(url, headers=request.headers)
        return response.json(), response.status_code

    @verify_jwt
    def post(self):
        """Add a new book (JWT protected)"""
        url = f"{BOOK_SERVICE_URL}"
        response = requests.post(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code

# Routes for Exchange Service (protected)
@exchange_ns.route('/<path:path>')
class ExchangeService(Resource):
    @verify_jwt
    def get(self, path):
        """Forward GET requests to the Exchange Service (JWT protected)"""
        url = f"{EXCHANGE_SERVICE_URL}/{path}"
        response = requests.get(url, headers=request.headers)
        return response.json(), response.status_code

    @verify_jwt
    def post(self, path):
        """Forward POST requests to the Exchange Service (JWT protected)"""
        url = f"{EXCHANGE_SERVICE_URL}/{path}"
        response = requests.post(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code

@exchange_ns.route('/')
class ExchangeServiceRoot(Resource):
    @verify_jwt
    def get(self):
        """Get all exchange requests (JWT protected)"""
        url = f"{EXCHANGE_SERVICE_URL}"
        response = requests.get(url, headers=request.headers)
        return response.json(), response.status_code

    @verify_jwt
    def post(self):
        """Create a new exchange request (JWT protected)"""
        url = f"{EXCHANGE_SERVICE_URL}"
        response = requests.post(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code

# Start the Flask app
if __name__ == '__main__':
    app.run(port=int(os.getenv('FLASK_RUN_PORT', 3000)))
