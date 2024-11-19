import os
import requests
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from functools import wraps
import jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
api = Api(app, doc='/docs', title="Booktrade API Gateway", description="API Gateway for Auth, Book, and Exchange Services")

# Load environment variables
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:3001')
BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL', 'http://localhost:3002')
EXCHANGE_SERVICE_URL = os.getenv('EXCHANGE_SERVICE_URL', 'http://localhost:3003')
JWT_SECRET = os.getenv('JWT_SECRET', 'your_jwt_secret')

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

# Define the input models for registration and login
auth_register_model = api.model('AuthRegister', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'name': fields.String(required=True, description='User name'),
})

auth_login_model = api.model('AuthLogin', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})


api.security = {'apikey': []}
api.authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

# Routes for Auth Service
@auth_ns.route('/register')
class AuthRegister(Resource):
    @api.expect(auth_register_model)  # Expect the auth_register_model here
    def post(self):
        """Register a new user"""
        url = f"{AUTH_SERVICE_URL}/api/register"
        response = requests.post(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code


@auth_ns.route('/login')
class AuthLogin(Resource):
    @api.expect(auth_login_model)  # Expect the auth_login_model here
    def post(self):
        """Log in and obtain a JWT"""
        url = f"{AUTH_SERVICE_URL}/api/login"
        response = requests.post(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code


@auth_ns.route('/profile')
class AuthProfile(Resource):
    @verify_jwt
    def get(self):
        """Retrieve user profile (JWT protected)"""
        url = f"{AUTH_SERVICE_URL}/api/profile"
        response = requests.get(url, headers=request.headers)
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

# Define the Exchange request model for Swagger
exchange_request_model = exchange_ns.model('ExchangeRequest', {
    'lender_id': fields.String(required=True, description='ID of the lender'),
    'borrower_id': fields.String(required=True, description='ID of the borrower'),
    'book_id': fields.String(required=True, description='ID of the book involved in the exchange'),
    'exchange_id': fields.Integer(required=True, description='Unique ID for the exchange request'),
    'status': fields.String(required=True, description='Status of the exchange request', enum=['pending', 'processing', 'completed', 'cancelled'])
})

# Define the model for updating the status
exchange_status_update_model = exchange_ns.model('ExchangeStatusUpdate', {
    'status': fields.String(required=True, description='New status for the exchange request', enum=['pending', 'processing', 'completed', 'cancelled'])
})

# Routes for Exchange Service (protected)
@exchange_ns.route('/api/exchange-requests')
class CreateExchangeRequest(Resource):
    @exchange_ns.expect(exchange_request_model, validate=True)
    @verify_jwt
    def post(self):
        """Create a new exchange request (JWT protected)"""
        url = f"{EXCHANGE_SERVICE_URL}/api/exchange-requests"
        response = requests.post(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code


@exchange_ns.route('/api/exchange-requests/<string:user_id>')
class ListExchangeRequestByUser(Resource):
    @verify_jwt
    def get(self, user_id):
        """List exchange requests for a specific user (JWT protected)"""
        url = f"{EXCHANGE_SERVICE_URL}/api/exchange-requests/{user_id}"
        response = requests.get(url, headers=request.headers)
        return response.json(), response.status_code


@exchange_ns.route('/api/exchange-requests/<int:exchange_id>')
class EditExchangeRequest(Resource):
    @exchange_ns.expect(exchange_status_update_model, validate=True)
    @verify_jwt
    def put(self, exchange_id):
        """Edit an exchange request by ID (JWT protected)"""
        url = f"{EXCHANGE_SERVICE_URL}/api/exchange-requests/{exchange_id}"
        response = requests.put(url, json=request.get_json(), headers=request.headers)
        return response.json(), response.status_code

    @verify_jwt
    def delete(self, exchange_id):
        """Delete an exchange request by ID (JWT protected)"""
        url = f"{EXCHANGE_SERVICE_URL}/api/exchange-requests/{exchange_id}"
        response = requests.delete(url, headers=request.headers)
        return response.json(), response.status_code



# Start the Flask app
if __name__ == '__main__':
    app.run(port=3000)
