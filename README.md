
# **API Gateway**

The **BookExchange API Gateway** serves as a centralized entry point for managing interactions between the Authentication, Book, and Exchange services. This gateway is implemented using Flask and Flask-RESTx, providing API routing, JWT-based authentication, and request delegation to microservices.

## **Table of Contents**

1. [Introduction](#introduction)
2. [Environment Setup](#environment-setup)
3. [Endpoints Overview](#endpoints-overview)
4. [How It Works](#how-it-works)
5. [Usage](#usage)

---

## **Introduction**

This API Gateway performs the following:
- Routes API requests to appropriate microservices.
- Secures endpoints with **JWT-based authentication**.
- Provides Swagger documentation for seamless API exploration (`/docs`).

Microservices:
1. **Auth Service**: Handles user registration, login, and profile management.
2. **Book Service**: Manages CRUD operations on books.
3. **Exchange Service**: Handles exchange requests for books.

---

## **Environment Setup**

### **Prerequisites**
- Python 3.8+
- `pip` for package management
- Environment variables configured in a `.env` file

### **Installation**

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and configure the following variables:
   ```
   AUTH_SERVICE_URL=http://localhost:3001
   BOOK_SERVICE_URL=http://localhost:3002
   EXCHANGE_SERVICE_URL=http://localhost:3003
   JWT_SECRET=your_jwt_secret
   ```

4. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:3000`.

---

## **Endpoints Overview**

### **Auth Service**
| Method | Endpoint          | Description                   |
|--------|-------------------|-------------------------------|
| POST   | `/auth/register`   | Registers a new user          |
| POST   | `/auth/login`      | Logs in a user and returns JWT|
| GET    | `/auth/profile`    | Retrieves user profile        |

### **Book Service**
| Method | Endpoint              | Description                            |
|--------|-----------------------|----------------------------------------|
| GET    | `/books`              | Retrieves all books                   |
| GET    | `/books/<book_id>`    | Retrieves a specific book by ID        |
| POST   | `/books`              | Adds a new book                        |
| PATCH  | `/books/<book_id>`    | Updates availability status of a book  |
| DELETE | `/books/<book_id>`    | Deletes a specific book by ID          |

### **Exchange Service**
| Method | Endpoint                           | Description                              |
|--------|-----------------------------------|------------------------------------------|
| POST   | `/exchange`                       | Creates a new exchange request           |
| GET    | `/exchange/user/<user_id>`        | Retrieves exchange requests for a user   |
| PUT    | `/exchange/<exchange_id>`         | Updates status of a specific exchange    |
| DELETE | `/exchange/<exchange_id>`         | Deletes a specific exchange request      |

---

## **How It Works**

1. **Request Routing**: Incoming API requests are routed to the relevant service based on the URL path.
   - `/auth/*` → **Auth Service**
   - `/books/*` → **Book Service**
   - `/exchange/*` → **Exchange Service**

2. **JWT Authentication**: Protected endpoints require a valid JWT token in the `Authorization` header:
   ```
   Authorization: Bearer <JWT_TOKEN>
   ```

3. **Service Communication**: Requests are proxied to the respective microservices:
   - Auth Service at `AUTH_SERVICE_URL`
   - Book Service at `BOOK_SERVICE_URL`
   - Exchange Service at `EXCHANGE_SERVICE_URL`

4. **Swagger Documentation**: Accessible at `/docs`, offering interactive API exploration.

---

## **Usage**

### **Authentication Example**
- **Register a User**:
  ```bash
  curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'
  ```

- **Login**:
  ```bash
  curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
  ```

### **Book Service Example**
- **Add a Book**:
  ```bash
  curl -X POST http://localhost:3000/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"title": "Book Title", "author": "Author Name", "genre": "Fiction", "publishedDate": "2023-01-01", "availability": true, "userId": "123"}'
  ```

### **Exchange Service Example**
- **Create Exchange Request**:
  ```bash
  curl -X POST http://localhost:3000/exchange \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"lender_id": "1", "borrower_id": "2", "book_id": "3", "exchange_id": "4", "status": "pending"}'
  ```

---
