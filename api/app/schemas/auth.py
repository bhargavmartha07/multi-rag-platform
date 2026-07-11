from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
    )


class UserRegisterResponse(BaseModel):

    id: int
    email: str
    tenant_id: str


class UserLoginRequest(BaseModel):

    email: EmailStr

    password: str


class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"


class UserMeResponse(BaseModel):

    id: int
    email: str
    tenant_id: str
