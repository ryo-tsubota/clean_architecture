from typing import List
from .repositories import ITodoItemRepository
from .dtos import CreateTodoDTO, TodoDTO
from domain.entities import TodoItem

class TodoUseCases:
    def __init__(self, repo: ITodoItemRepository):
        self.repo = repo

    def create_todo(self, dto: CreateTodoDTO) -> TodoDTO:
        todo = TodoItem(title=dto.title)
        created_todo = self.repo.save(todo)
        return TodoDTO.from_orm(created_todo)

    def get_all_todos(self) -> List[TodoDTO]:
        todos = self.repo.find_all()
        return [TodoDTO.from_orm(t) for t in todos]

    def complete_todo(self, todo_id: str) -> TodoDTO:
        todo = self.repo.find_by_id(todo_id)
        if not todo:
            raise ValueError("Todo not found")
        
        completed_todo_entity = todo.mark_as_completed()
        updated_todo = self.repo.save(completed_todo_entity)
        return TodoDTO.from_orm(updated_todo)