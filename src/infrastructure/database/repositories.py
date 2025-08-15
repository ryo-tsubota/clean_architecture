from typing import List, Optional
from domain.entities import TodoItem
from application.repositories import ITodoItemRepository

class InMemoryTodoRepository(ITodoItemRepository):
    def __init__(self):
        self._todos: dict[str, TodoItem] = []
    

    def save(self, todo: TodoItem) -> TodoItem:
        self._todos[todo.id] = todo
        return todo
    
    def find_by_id(self, id: str) -> Optional[TodoItem]:
        return self._todos.get(id)
    
    def find_all(self) -> List[TodoItem]:
        return list(self._todos.values())

from sqlalchemy.orm import Session
from .models import TodoItemModel
class SqlAlchemyTodoItemRepository(ITodoItemRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, todo: TodoItem) -> TodoItem:
        model = self.session.query(TodoItemModel).filter(TodoItemModel.id == todo.id).first()
        if model is None:
            model = TodoItemModel(id=todo.id, title=todo.title, completed=todo.completed)
        else:
            model.title = todo.title
            model.completed = todo.completed
        
        self.session.add(model)
        self.session.commit()
        return todo

    def find_by_id(self, todo_id: str) -> Optional[TodoItem]:
        model = self.session.query(TodoItemModel).filter(TodoItemModel.id == todo_id).first()
        if model:
            return TodoItem(id=model.id, title=model.title, completed=model.completed)
        return None

    def find_all(self) -> List[TodoItem]:
        models = self.session.query(TodoItemModel).all()
        return [TodoItem(id=m.id, title=m.title, completed=m.completed) for m in models]