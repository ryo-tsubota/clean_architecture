from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TodoItemModel(Base):
    __tablename__ = "todos"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    completed = Column(Boolean, default=False)