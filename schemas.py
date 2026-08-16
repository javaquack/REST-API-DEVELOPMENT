import re
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

# Regex for basic email verification without requiring email-validator library
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# User Schemas
class UserBase(BaseModel):
    email: str = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name of the user")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not EMAIL_REGEX.match(v_clean):
            raise ValueError("Invalid email format")
        return v_clean


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Password (min 6 characters)")


class UserLogin(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Detailed product description")
    price: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2, description="Price of the product (must be greater than 0)")
    stock: int = Field(..., ge=0, description="Stock quantity (must be 0 or more)")
    category: Optional[str] = Field(None, max_length=100, description="Category tag")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=Decimal("0.00"), decimal_places=2)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)


class ProductOut(ProductBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
