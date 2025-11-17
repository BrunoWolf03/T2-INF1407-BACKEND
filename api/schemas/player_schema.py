from pydantic import BaseModel

class PlayerSchema(BaseModel):
    id: int | None = None
    name: str
    score: float

    class Config:
        orm_mode = True
