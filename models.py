# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship

# from .database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Book(BaseModel):
  id: Optional[int] = None
  title: str
  synopsis: str
  author: str
