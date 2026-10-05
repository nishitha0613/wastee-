import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.user import UserRole

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Jane Doe")
    email: str = Field(..., example="jane.doe@example.com")
    role: UserRole = Field(default=UserRole.USER, example="user")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Invalid email address format")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, example="securepassword123")


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Example User")
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, max_length=128, example="password123")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Invalid email address format")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v


class UserLogin(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=1, example="password123")

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        return v.strip().lower()


class UserBasicInfo(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBasicInfo
