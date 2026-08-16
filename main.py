from contextlib import asynccontextmanager
from typing import List, Optional
from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, IntegrityError

import models
import schemas
import crud
import auth
from database import engine, get_db

# Lifespan manager to handle startup/shutdown tasks gracefully
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Attempt connection and table creation at startup
    try:
        models.Base.metadata.create_all(bind=engine)
        print("Database connection established and tables synchronized successfully.")
    except OperationalError as e:
        print("\n" + "="*80)
        print("DATABASE WARNING: Could not connect to MySQL server at startup.")
        print("The API is running, but database connection endpoints will fail until MySQL is running.")
        print(f"Details: {e}")
        print("="*80 + "\n")
    yield

# Define FastAPI application metadata
app = FastAPI(
    title="Kinetrexa REST API",
    description="A robust and secure Python RESTful API built with FastAPI, MySQL, JWT authentication, and Pydantic validation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for standard web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins, customize in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Custom Exception Handlers ---

@app.exception_handler(OperationalError)
def db_operational_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database server is unavailable. Please verify MySQL configuration and check connection status."}
    )


# --- Root Endpoint ---

@app.get("/", tags=["General"])
def read_root():
    return {
        "message": "Welcome to the Kinetrexa API!",
        "status": "Online",
        "documentation": "/docs",
        "database_type": "MySQL"
    }


# --- Authentication & User Endpoints ---

@app.post("/api/v1/auth/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account with secure password hashing.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    return crud.create_user(db=db, user=user)


@app.post("/api/v1/auth/login", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Authenticate user via credentials and return JWT bearer token.
    Uses Standard Form Authentication parameters to integrate with Swagger documentation.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Exclude password in payload; include user identity
    access_token = auth.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/v1/auth/me", response_model=schemas.UserOut, tags=["Authentication"])
def read_user_profile(current_user: models.User = Depends(auth.get_current_user)):
    """
    Retrieve authenticated user profile detail.
    """
    return current_user


# --- Products Resource Endpoints (CRUD) ---

@app.post("/api/v1/products", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create a new product listing. Requires JWT Bearer Token in authorization headers.
    """
    return crud.create_user_product(db=db, product=product, user_id=current_user.id)


@app.get("/api/v1/products", response_model=List[schemas.ProductOut], tags=["Products"])
def list_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max number of products to return"),
    category: Optional[str] = Query(None, description="Filter products by category name"),
    db: Session = Depends(get_db)
):
    """
    Retrieve products catalog with customizable offset/limit pagination and category filter. Public access.
    """
    return crud.get_products(db=db, skip=skip, limit=limit, category=category)


@app.get("/api/v1/products/{product_id}", response_model=schemas.ProductOut, tags=["Products"])
def get_product_details(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieve single product specifications by product ID. Public access.
    """
    db_product = crud.get_product(db=db, product_id=product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return db_product


@app.put("/api/v1/products/{product_id}", response_model=schemas.ProductOut, tags=["Products"])
def update_product_details(
    product_id: int, 
    product_update: schemas.ProductUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Modify an existing product listing. Owner validation required.
    """
    db_product = crud.get_product(db=db, product_id=product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Ownership authorization check
    if db_product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this product listing"
        )
        
    return crud.update_product(db=db, db_product=db_product, product_update=product_update)


@app.delete("/api/v1/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def remove_product(
    product_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Delete a product listing. Owner validation required.
    """
    db_product = crud.get_product(db=db, product_id=product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Ownership authorization check
    if db_product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this product listing"
        )
        
    crud.delete_product(db=db, db_product=db_product)
    return None