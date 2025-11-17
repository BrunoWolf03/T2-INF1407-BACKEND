from pydantic import BaseModel

class PlayerCreate(BaseModel):
    id: int
    first_name: str
    last_name: str
    position: str | None = None
    team: str | None = None


class PlayerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    position: str | None
    team: str | None

    class Config:
        from_attributes = True  # antes era orm_mode=True
