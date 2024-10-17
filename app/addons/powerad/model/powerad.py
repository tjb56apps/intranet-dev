from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Servers(Base):
    __tablename__ = "Servers"

    id = Column(Integer, primary_key=True)
    domain = Column(String)
    port = Column(Integer)
    status = Column(Integer)

    def __repr__(self):
        return f"Servers {self.domain}"
    
class DataServer(Base):
    __tablename__ = "Dataserver"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(255))
    dcserver = Column(String(50))
    oubase = Column(String(50))
    server = Column(String(50))

    def __repr__(self):
        return f"DataServer {self.username}"