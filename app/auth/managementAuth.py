from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    department = Column(String)
    position = Column(String)
    email = Column(String)
    username = Column(String)
    password = Column(String)
    apps_id = Column(String)
    level = Column(String)
    type = Column(String)
    domain = Column(String)
    leveling = Column(String)

    def __repr__(self):
        return f"Users <{self.name}>"