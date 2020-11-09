from pydantic import BaseModel


class Role(BaseModel):
    id: str

    class Config:
        orm_mode = True
