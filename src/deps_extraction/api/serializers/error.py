from pydantic import BaseModel


class ErrorSerializer(BaseModel):
    code: str
    message: str
