from pydantic import EmailStr, BaseModel
from typing import Annotated
from annotated_types import MinLen, MaxLen


class CreateUser(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(130)]
    email: EmailStr
