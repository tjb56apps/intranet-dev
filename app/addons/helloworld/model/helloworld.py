# from app.extensions import db
# from app.extensions.database import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Blogpost(Base):
    __tablename__ = "helloworld"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)

    def __repr__(self):
        return f"<Post {self.title}>"