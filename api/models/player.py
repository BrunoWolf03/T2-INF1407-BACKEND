from sqlalchemy import Column, Integer, String
from api.database.connection import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    position = Column(String)
    team = Column(String)
    score = Column(Integer)
