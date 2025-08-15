from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import TodoItem

class ITodoItemRepository(ABC):
    @abstractmethod
    def save(self, todo: TodoItem) -> TodoItem:
        pass

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[TodoItem]:
        pass

    @abstractmethod
    def find_all(self) -> List[TodoItem]:
        pass


