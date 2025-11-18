from pydantic import BaseModel

class PlayerSchema(BaseModel):
    id: int
    name: str
    position: str
    team: str
    score: int

    class Config:
        orm_mode = True
