import uuid
from dataclasses import dataclasses, field
from typing import Optional

@dataclasses
class TodoItem:
    title: str
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


    def mark_as_completed(self) -> "TodoItem":
        if self.completed:
            raise ValueError("タスクは既に完了しています。")
        return TodoItem(id = self.id, title=self.title, completed=True)