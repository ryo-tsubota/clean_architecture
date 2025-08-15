# 練習問題3: Python実装パターン編

## 問題3-1: Dataclassとバリデーション

以下の要件でProductエンティティを実装してください。

**要件:**
- 商品ID、名前、価格、カテゴリIDは必須
- 価格は0以上でなければならない
- 名前は空文字列や空白のみは不可
- 作成日時は自動で設定される
- 値オブジェクトパターンを使って価格を表現する

**課題:**
1. `Price`値オブジェクトを作成してください
2. `Product`エンティティをdataclassで実装してください
3. バリデーションは`__post_init__`で行ってください

```python
# ヒント: 開始コード
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

@dataclass(frozen=True)
class Price:
    # TODO: 実装してください
    pass

@dataclass
class Product:
    # TODO: 実装してください
    pass
```

## 問題3-2: Protocolを使ったインターフェース設計

PythonのProtocolを使って、型安全なリポジトリインターフェースを実装してください。

**要件:**
- ジェネリック型を使って汎用的なリポジトリを作成
- mypy チェックが通るように型ヒントを適切に設定
- 実装クラスでのメソッドシグネチャミスを検出できるように

**課題:**
```python
from typing import Protocol, TypeVar, Generic, List, Optional

T = TypeVar('T')
ID = TypeVar('ID')

# TODO: Repository Protocol を実装してください
class Repository(Protocol, Generic[T, ID]):
    pass

# TODO: UserRepository の具体的なProtocol を実装してください
class UserRepository(Protocol):
    pass

# TODO: インメモリ実装を作成し、型チェックが正しく動作することを確認
class InMemoryUserRepository:
    pass
```

## 問題3-3: 依存性注入の実装

dependency-injectorを使わずに、シンプルなDIコンテナを実装してください。

**要件:**
- コンストラクタインジェクション
- インターフェース（Protocol）に基づく注入
- シングルトンスコープとトランジェントスコープ
- 循環依存の検出

**課題:**
```python
from typing import TypeVar, Type, Callable, Dict, Any
from enum import Enum

class Scope(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"

T = TypeVar('T')

class DIContainer:
    def __init__(self):
        # TODO: 実装してください
        pass
    
    def register(self, interface: Type[T], implementation: Type, scope: Scope = Scope.TRANSIENT):
        # TODO: 実装してください
        pass
    
    def resolve(self, interface: Type[T]) -> T:
        # TODO: 実装してください
        pass

# 使用例をテストできるコードも作成してください
```

## 問題3-4: 非同期処理とクリーンアーキテクチャ

非同期処理を使ったメール送信サービスを実装してください。

**要件:**
- EmailServiceはabstractbaseクラス
- SMTPとAWS SESの実装を作成
- 非同期バッチ処理に対応
- エラーハンドリングとリトライ機能

**課題:**
```python
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

@dataclass
class Email:
    to: str
    subject: str
    body: str
    from_email: Optional[str] = None

class EmailStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

# TODO: EmailService を実装してください
class EmailService(ABC):
    pass

# TODO: SMTP実装を作成してください
class SMTPEmailService(EmailService):
    pass

# TODO: AWS SES実装を作成してください  
class SESEmailService(EmailService):
    pass

# TODO: バッチ処理可能なEmailSender を作成してください
class EmailSender:
    pass
```

## 問題3-5: カスタム例外とエラーハンドリング

クリーンアーキテクチャに適したエラーハンドリング体系を実装してください。

**要件:**
- ドメイン例外、アプリケーション例外、インフラ例外の階層
- エラーコードとメッセージの管理
- 国際化対応
- ログ出力機能

**課題:**
```python
from abc import ABC
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, Any
import logging

class ErrorCode(Enum):
    # TODO: エラーコードを定義してください
    pass

@dataclass
class ErrorContext:
    # TODO: エラーコンテキストを定義してください
    pass

# TODO: 基底例外クラスを実装してください
class CleanArchitectureException(Exception, ABC):
    pass

# TODO: ドメイン例外を実装してください
class DomainException(CleanArchitectureException):
    pass

# TODO: アプリケーション例外を実装してください
class ApplicationException(CleanArchitectureException):
    pass

# TODO: インフラ例外を実装してください  
class InfrastructureException(CleanArchitectureException):
    pass

# TODO: エラーハンドラーを実装してください
class ErrorHandler:
    pass
```

## 問題3-6: イベント駆動アーキテクチャ

ドメインイベントを使ったイベント駆動システムを実装してください。

**要件:**
- ドメインイベントの基底クラス
- イベント発行・購読の仕組み
- 非同期イベントハンドリング
- イベントストア（オプション）

**課題:**
```python
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Callable, Dict, Type, Any
from uuid import uuid4

# TODO: ドメインイベントの基底クラスを実装
@dataclass
class DomainEvent(ABC):
    pass

# TODO: 具体的なイベントの例を作成
@dataclass
class UserCreatedEvent(DomainEvent):
    pass

@dataclass  
class OrderPlacedEvent(DomainEvent):
    pass

# TODO: イベントハンドラーのインターフェース
class EventHandler(ABC):
    pass

# TODO: イベントディスパッチャーを実装
class EventDispatcher:
    pass

# TODO: 使用例とテストケースを作成
```

## 問題3-7: パフォーマンス最適化

大量データを扱う際のパフォーマンス最適化パターンを実装してください。

**要件:**
- Repository層でのページネーション
- レイジーローディング
- キャッシュ層の抽象化
- バルク操作のサポート

**課題:**
```python
from typing import List, Optional, AsyncIterator, TypeVar, Generic
from dataclasses import dataclass
from abc import ABC, abstractmethod

T = TypeVar('T')

@dataclass
class PageInfo:
    page: int
    size: int
    total: int
    has_next: bool

@dataclass  
class PagedResult(Generic[T]):
    items: List[T]
    page_info: PageInfo

# TODO: ページネーション対応リポジトリを実装
class PagedRepository(ABC, Generic[T]):
    pass

# TODO: キャッシュインターフェース を実装
class Cache(ABC):
    pass

# TODO: キャッシュ機能付きリポジトリを実装
class CachedRepository(Generic[T]):
    pass

# TODO: バルク操作インターフェースを実装
class BulkRepository(ABC, Generic[T]):
    pass
```

---

## 解答例

### 問題3-1の解答例

```python
@dataclass(frozen=True)
class Price:
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("価格は0以上である必要があります")
    
    def __str__(self) -> str:
        return f"¥{self.value:,}"

@dataclass
class Product:
    name: str
    price: Price
    category_id: str
    product_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.name or self.name.strip() == "":
            raise ValueError("商品名は必須です")
        if not self.category_id:
            raise ValueError("カテゴリIDは必須です")
```

### 問題3-2の解答例

```python
class Repository(Protocol, Generic[T, ID]):
    def save(self, entity: T) -> T: ...
    def find_by_id(self, id: ID) -> Optional[T]: ...
    def find_all(self) -> List[T]: ...
    def delete(self, id: ID) -> bool: ...

class UserRepository(Protocol):
    def save(self, user: User) -> User: ...
    def find_by_id(self, user_id: str) -> Optional[User]: ...
    def find_by_email(self, email: str) -> Optional[User]: ...
```