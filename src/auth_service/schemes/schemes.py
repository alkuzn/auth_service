from pydantic import BaseModel, EmailStr, field_validator


class RegisterData(BaseModel):
    email: EmailStr
    # @field_validator('email', mode='plain')
    # def main(cls, value):
    #    try:
    #        ta = TypeAdapter(EmailStr).validate_strings(value)
    #        return ta
    #    except ValidationError as ex:
    #        raise HTTPException(
    #        status_code=status.HTTP_400_BAD_REQUEST,
    #        detail="Неверный формат email."
    #        )


class ResponseData(BaseModel):
    pass


class Error(BaseModel):
    pass


from pydantic import ConfigDict, TypeAdapter, ValidationError
