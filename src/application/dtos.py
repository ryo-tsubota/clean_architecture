from pydantic import BaseModel

class CreateTodoDTO(BaseModel):
    title: str

class TodoDTO(BaseModel):
    id: str
    title: str
    completed: bool

    class Config:
        orm_mode = True # EntityからPydanticモデルへの変換を容易にする