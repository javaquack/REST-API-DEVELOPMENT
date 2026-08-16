from typing import Optional, List
from sqlalchemy.orm import Session
import models
import schemas
import auth

# --- User CRUD Operations ---

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Retrieve a single user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Retrieve a single user by email address."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with a hashed password."""
    hashed_pwd = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_pwd,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Product CRUD Operations ---

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    """Retrieve a single product by ID."""
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products(
    db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None
) -> List[models.Product]:
    """Retrieve products list with pagination and optional category filter."""
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    return query.offset(skip).limit(limit).all()


def create_user_product(db: Session, product: schemas.ProductCreate, user_id: int) -> models.Product:
    """Create a new product owned by a specific user."""
    # Convert Pydantic fields to SQLAlchemy model arguments
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category=product.category,
        owner_id=user_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, db_product: models.Product, product_update: schemas.ProductUpdate) -> models.Product:
    """Update attributes of an existing product dynamically based on fields supplied."""
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, db_product: models.Product) -> None:
    """Delete a product from the database."""
    db.delete(db_product)
    db.commit()
