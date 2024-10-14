from pydantic import BaseModel, Field
from ..users.schema import UserItem


class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "javier@foreach.cl",
                "password": "123",
            }
        }


class RecoverPasswordSchema(BaseModel):
    email: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "test@test.cl",
            }
        }


class PasswordChangeSchema(BaseModel):
    new_password: str = Field(alias="newPassword")
    recovery_token: str = Field(alias="recoveryToken")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "new_password": "1234567890",
                "recoveryToken": "asdhuashdujasd78as6f78as6d78ya7sdasd",
            }
        }


class ChangePasswordSchema(BaseModel):
    new_pass: str
    current_pass: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "current_pass": "1234567890",
                "new_pass": "1234567890",
            }
        }


class RecoveryTokenSchema(BaseModel):
    recovery_token: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "recovery_token": "3452fsdfsd8f7sd89f7sd89fusdfsdfse",
            }
        }


class MeResponseSchema(UserItem):
    class Config:
        orm_mode = True


class LoginUser(BaseModel):
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    user: UserItem

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {
            str: lambda v: v
        }
