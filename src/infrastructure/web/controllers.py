from fastapi import APIRouter, Depends
from typing import List
from dependency_injector.wiring import inject, Provide

from application.use_cases import TodoUseCases
from application.dtos import CreateTodoDTO, TodoDTO
from container import Container

router = APIRouter()

@router.post("/todos", response_model=TodoDTO)
@inject
def create_todo(
    dto: CreateTodoDTO,
    use_cases: TodoUseCases = Depends(Provide[Container.todo_use_cases])
):
    return use_cases.create_todo(dto)

@router.get("/todos", response_model=List[TodoDTO])
@inject
def get_all_todos(
    use_cases: TodoUseCases = Depends(Provide[Container.todo_use_cases])
):
    return use_cases.get_all_todos()

@router.post("/todos/{todo_id}/complete", response_model=TodoDTO)
@inject
def complete_todo(
    todo_id: str,
    use_cases: TodoUseCases = Depends(Provide[Container.todo_use_cases])
):
    try:
        return use_cases.complete_todo(todo_id)
    except ValueError as e:
        # エラーハンドリングは別途ミドルウェアで実装するのが望ましい
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))