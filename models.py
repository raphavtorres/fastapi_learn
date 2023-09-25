from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Book(Base):
  __tablename__ = "books"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, unique=True)
  author = Column(String)
  synopsis = Column(String)
