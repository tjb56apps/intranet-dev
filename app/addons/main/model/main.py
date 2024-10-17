from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# navigation
class Nav(Base):
    __tablename__ = "nav"
    
    id = Column(Integer, primary_key=True)
    app_id = Column(String(10))
    name = Column(String(50))
    version = Column(String(10))
    status = Column(Integer)
    path = Column(String(50))
    nav = Column(String(255))

    def __repr__(self):
        return f"Nav <{self.name}>"