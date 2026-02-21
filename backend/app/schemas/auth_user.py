from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    first_name: str
    last_name: str
    age: int
    gender: str
    phone: str
    email: EmailStr
    password: str

class LoginUser(BaseModel):
    email: EmailStr
    password: str