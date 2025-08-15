# 第4章: 実践: ToDoリストAPIの構築

これまでの章で学んだ理論とパターンを総動員して、簡単な「ToDoリスト管理API」をクリーンアーキテクチャで構築してみましょう。この実践的な演習を通して、各レイヤーがどのように連携し、依存性のルールがどのように守られるのかを体感します。

使用する主なライブラリは以下の通りです。
*   Webフレームワーク: **FastAPI**
*   ORM: **SQLAlchemy**
*   DIコンテナ: **dependency-injector**

## 4-1. プロジェクトのセットアップ

まず、プロジェクトのディレクトリ構造を第3章で学んだ形に整え、必要なライブラリをインストールします。

**1. ディレクトリ構造の作成**

```
clean_architecture/
├── src/
│   ├── __init__.py
│   ├── domain/
│   │   └── entities.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── use_cases.py
│   │   ├── repositories.py
│   │   └── dtos.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── repositories.py
│   │   └── web/
│   │       ├── __init__.py
│   │       └── controllers.py
│   ├── container.py
│   └── main.py
└── requirements.txt
```

**2. ライブラリのインストール**

`requirements.txt` に以下を記述し、インストールします。

```txt
fastapi
uvicorn[standard]
SQLAlchemy
dependency-injector
pydantic
```

```bash
pip install -r requirements.txt
```

## 4-2. Entityの定義 (`TodoItem`)

最初に、ビジネスの核となるエンティティを定義します。

`src/domain/entities.py`
```python
import uuid
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TodoItem:
    title: str
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_as_completed(self) -> "TodoItem":
        if self.completed:
            raise ValueError("タスクは既に完了しています")
        return TodoItem(id=self.id, title=self.title, completed=True)
```

## 4-3. Repositoryインターフェースと実装

次に、ユースケース層がデータを操作するための「窓口」となるリポジトリインターフェースを定義し、その実装を作成します。

#### 1. Repositoryインターフェース (Port) の定義

`src/application/repositories.py`
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import TodoItem

class ITodoItemRepository(ABC):
    @abstractmethod
    def save(self, todo: TodoItem) -> TodoItem:
        pass

    @abstractmethod
    def find_by_id(self, todo_id: str) -> Optional[TodoItem]:
        pass

    @abstractmethod
    def find_all(self) -> List[TodoItem]:
        pass
```

#### 2. インメモリ実装 (テストや開発初期段階で便利)

`src/infrastructure/database/repositories.py` (ファイル上部)
```python
from typing import List, Optional
from src.domain.entities import TodoItem
from src.application.repositories import ITodoItemRepository

class InMemoryTodoItemRepository(ITodoItemRepository):
    def __init__(self):
        self._todos: dict[str, TodoItem] = {}

    def save(self, todo: TodoItem) -> TodoItem:
        self._todos[todo.id] = todo
        return todo

    def find_by_id(self, todo_id: str) -> Optional[TodoItem]:
        return self._todos.get(todo_id)

    def find_all(self) -> List[TodoItem]:
        return list(self._todos.values())
```

#### 3. データベース実装 (SQLAlchemy)

まず、ORMモデルを定義します。

`src/infrastructure/database/models.py`
```python
from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TodoItemModel(Base):
    __tablename__ = "todos"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    completed = Column(Boolean, default=False)
```

次に、リポジトリインターフェースを実装します。

`src/infrastructure/database/repositories.py` (ファイル下部)
```python
from sqlalchemy.orm import Session
# ... (他のimport)

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
```

## 4-4. Use Case (Interactor) と DTO の作成

アプリケーションのロジックを実装します。

#### 1. DTOの定義

`src/application/dtos.py`
```python
from pydantic import BaseModel

class CreateTodoDTO(BaseModel):
    title: str

class TodoDTO(BaseModel):
    id: str
    title: str
    completed: bool

    class Config:
        orm_mode = True # EntityからPydanticモデルへの変換を容易にする
```

#### 2. Use Caseの作成

`src/application/use_cases.py`
```python
from typing import List
from .repositories import ITodoItemRepository
from .dtos import CreateTodoDTO, TodoDTO
from src.domain.entities import TodoItem

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
```

## 4-5. Controller (APIエンドポイント) の実装

FastAPIを使って、Webからのリクエストを受け付ける口を作成します。

`src/infrastructure/web/controllers.py`
```python
from fastapi import APIRouter, Depends
from typing import List
from dependency_injector.wiring import inject, Provide

from src.application.use_cases import TodoUseCases
from src.application.dtos import CreateTodoDTO, TodoDTO
from src.container import Container

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
```

## 4-6. DIコンテナとアプリケーションの起動

最後に、これら全てのコンポーネントをDIコンテナで結合し、FastAPIアプリケーションを起動します。

#### 1. DIコンテナの定義

`src/container.py`
```python
from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.application.repositories import ITodoItemRepository
from src.infrastructure.database.repositories import SqlAlchemyTodoItemRepository
from src.application.use_cases import TodoUseCases
from src.infrastructure.database.models import Base

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.db_url.from_env("DATABASE_URL", "sqlite:///./test.db")

    engine = providers.Singleton(create_engine, url=config.db_url)
    db_session_factory = providers.Factory(sessionmaker, bind=engine, autocommit=False, autoflush=False)

    # --- Repository --- 
    # 状況に応じて InMemoryTodoItemRepository と切り替え可能
    todo_repository: providers.Provider[ITodoItemRepository] = providers.Factory(
        SqlAlchemyTodoItemRepository,
        session=db_session_factory,
    )

    # --- Use Cases ---
    todo_use_cases: providers.Provider[TodoUseCases] = providers.Factory(
        TodoUseCases,
        repo=todo_repository,
    )

    # DBの初期化
    @staticmethod
    def create_db_tables(engine):
        Base.metadata.create_all(bind=engine)
```

#### 2. アプリケーションのエントリーポイント

`src/main.py`
```python
from fastapi import FastAPI
from dependency_injector.wiring import inject

from src.container import Container
from src.infrastructure.web import controllers

@inject
def create_app() -> FastAPI:
    container = Container()
    container.wire(modules=[controllers])

    # DBテーブルの作成
    container.create_db_tables(container.engine())

    app = FastAPI()
    app.container = container
    app.include_router(controllers.router)
    return app

app = create_app()
```

これで、クリーンアーキテクチャに基づいたToDo APIの完成です！ `uvicorn src.main:app --reload` コマンドでサーバーを起動し、動作を確認できます。
