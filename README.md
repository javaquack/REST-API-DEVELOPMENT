# Kinetrexa REST API

A secure, high-performance RESTful API built with **FastAPI**, **SQLAlchemy ORM**, and **MySQL**. It features JWT authentication, strict input validation using Pydantic, proper error handling, automatic OpenAPI/Swagger documentation, and full CRUD operations for a Product Management catalog.

## Key Features
- **REST API Architecture**: Follows industry-standard REST principles and status codes.
- **CRUD Operations**: Complete Create, Read, Update, and Delete endpoints for a `Product` resource.
- **JWT Authentication**: Secure user registration, credential validation, password hashing (via `bcrypt`), and JSON Web Token (JWT) issuance.
- **Input Validation**: Automatic request payload filtering and validation using Pydantic v2.
- **Access Control**: Users can browse public catalogs but can only update or delete products they created.
- **Error Handling**: Graceful exception handling for common database and validation exceptions.
- **API Documentation**: Interactive documentation page auto-generated out of the box.

---

## Tech Stack
- **Language**: Python 3.8+ (tested on Python 3.13)
- **Framework**: FastAPI
- **Server**: Uvicorn
- **ORM**: SQLAlchemy
- **Database Driver**: PyMySQL
- **Database**: MySQL
- **Security**: PyJWT/python-jose (JWT tokens), bcrypt (password hashing)
- **Deployment**: Render

---

## Getting Started

### 1. Database Setup
1. Open your MySQL client (e.g., Command Line, MySQL Workbench, phpMyAdmin).
2. Create a new database named `kinetrexa_db`:
   ```sql
   CREATE DATABASE kinetrexa_db;
   ```

### 2. Installation
Clone or navigate to the project directory, then install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create or edit the `.env` file in the root directory. Configure your MySQL credentials and security parameters:
```env
# Database URI: mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost:3306/kinetrexa_db

# Security Settings
SECRET_KEY=45d8a6e87f8bb93c20ad41e06d91bb39ad0ef5d9d7fbe8cbcd577a7605d8f69d
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
> **Note:** Replace `YOUR_MYSQL_PASSWORD` with the root or user password you set during the MySQL Server installation.

### 4. Running the API Server
Start the Uvicorn server in development mode:
```bash
uvicorn main:app --reload
```
Once started, the server will run on `http://127.0.0.1:8000`.

---

## API Documentation & Exploration

FastAPI automatically generates interactive Swagger documentation:
- **Swagger UI**: Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser. You can register, login, and run requests directly from the UI.
- **ReDoc**: Alternative documentation representation at [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

---

## API Endpoints List

### Authentication
- `POST /api/v1/auth/register` - Registers a new user.
- `POST /api/v1/auth/login` - Authenticates user credentials and returns a JWT access token.
- `GET /api/v1/auth/me` - Retrieves the authenticated user's profile (requires bearer token).

### Products Catalog
- `GET /api/v1/products` - Returns a list of products (Public, supports pagination and category filtering).
- `GET /api/v1/products/{id}` - Returns detail specifications for a single product (Public).
- `POST /api/v1/products` - Creates a new product listing (Requires JWT token).
- `PUT /api/v1/products/{id}` - Updates product fields (Requires JWT token; owner-only access).
- `DELETE /api/v1/products/{id}` - Removes a product listing from the system (Requires JWT token; owner-only access).

---

## Postman Integration

A ready-to-import Postman Collection file `postman_collection.json` is provided in the project folder.

### Importing the Collection:
1. Open Postman.
2. Click **Import** at the top left.
3. Select `postman_collection.json` from the project folder.
4. Once imported, the collection contains two folders: **Authentication** and **Products**.
5. Log in using the **User Login** request. The Postman collection contains a script that automatically saves the JWT access token to the collection variables, meaning you do not have to copy-paste the token manually to run subsequent requests.

---

## Deployment to Render

This project includes a `render.yaml` Blueprint for automated deployment to [Render](https://render.com).

### Prerequisites
- A **hosted MySQL database** (Render does not provide MySQL natively). You can use a free-tier MySQL provider such as:
  - [Clever Cloud](https://www.clever-cloud.com/)
  - [Aiven](https://aiven.io/)
  - [Railway](https://railway.app/)
  - [FreeSQLDatabase](https://www.freesqldatabase.com/)

### Deployment Steps
1. **Push your code** to GitHub (this repository).
2. Go to [https://dashboard.render.com](https://dashboard.render.com) and sign in.
3. Click **New** > **Web Service**.
4. Connect your GitHub repository (`javaquack/REST-API-DEVELOPMENT`).
5. Render will auto-detect the `render.yaml` configuration. If not, manually configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Under the **Environment** tab, add the following environment variables:
   - `DATABASE_URL` — Your hosted MySQL connection string (e.g., `mysql+pymysql://user:pass@host:port/dbname`)
   - `SECRET_KEY` — A secure random string for JWT signing
   - `ALGORITHM` — `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` — `60`
7. Click **Deploy**. Render will install dependencies and start the server.
8. Once deployed, your API will be accessible at `https://your-service-name.onrender.com/docs`.
