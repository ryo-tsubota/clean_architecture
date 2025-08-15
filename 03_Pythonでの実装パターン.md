# 第3章: Pythonでの実装パターン

クリーンアーキテクチャの理論と各レイヤーの責務を理解したところで、次はその理論を実際のPythonコードに落とし込むための具体的な実装パターンを見ていきましょう。この章では、依存性のルールを強制するための「依存性逆転の原則」、依存関係を解決する「DI」、そしてプロジェクト全体の構造について学びます。

## 3-1. 依存性逆転の原則 (DIP) とは

依存性逆転の原則（Dependency Inversion Principle）は、SOLID原則の一つであり、クリーンアーキテクチャの「依存性のルール」を実現するための技術的な支柱です。

DIPは2つの要点からなります。

1.  **上位モジュールは、下位モジュールに依存してはならない。両者とも、抽象に依存すべきである。**
2.  **抽象は、詳細に依存してはならない。詳細は、抽象に依存すべきである。**

これをクリーンアーキテクチャの文脈に当てはめてみましょう。

*   **上位モジュール**: ユースケース層（ビジネスロジック）
*   **下位モジュール**: インターフェースアダプター層（DB実装など）
*   **抽象**: ユースケース層が定義するインターフェース（抽象基底クラス）
*   **詳細**: インターフェースアダプター層が実装する具象クラス

つまり、「ユースケース層は、具体的なDB実装のクラスを直接知るべきではない。代わりに、ユースケース層自身が『こういう機能を持ったリポジトリが欲しい』というインターフェース（抽象）を定義し、DB実装（詳細）はそのインターフェースを実装するべきである」ということです。

**Pythonでの実装:**
Pythonでは、この「抽象」を `abc` (Abstract Base Classes) モジュールを使って表現します。

```python
# --- ユースケース層 (上位モジュール) --- 
from abc import ABC, abstractmethod

# 「抽象」としてのリポジトリインターフェースを定義
class IUserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> User:
        pass

# ユースケースは具象クラスではなく、この「抽象」に依存する
class GetUserUseCase:
    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def execute(self, user_id: str) -> User:
        return self.repository.find_by_id(user_id)

# --- インターフェースアダプター層 (下位モジュール) --- 

# 「詳細」であるDB実装クラスが、「抽象」を実装(継承)する
class UserRepositoryImpl(IUserRepository):
    def find_by_id(self, user_id: str) -> User:
        # ここに具体的なDBアクセス処理を書く
        print(f"データベースからユーザー({user_id})を検索しました")
        # ...
        return User(id=user_id, name="Taro Yamada")
```

このように、依存の方向が `UserRepositoryImpl` → `IUserRepository` となり、本来の流れ（ユースケースがDB実装に依存する）とは逆転しています。これが「依存性逆転」です。

## 3-2. DI (Dependency Injection) の基本

依存性逆転の原則を使うと、新たな疑問が生まれます。「`GetUserUseCase` は `IUserRepository` を必要としているが、実際に動く `UserRepositoryImpl` のインスタンスは、一体誰が `GetUserUseCase` に渡すのか？」

この問いに答えるのが **DI (Dependency Injection / 依存性の注入)** です。

DIとは、あるオブジェクトが必要とする別のオブジェクト（依存オブジェクト）を、外部から与える（注入する）デザインパターンです。

#### コンストラクタインジェクション

最も基本的で推奨されるDIの方法が「コンストラクタインジェクション」です。これは、オブジェクトのコンストラクタ（`__init__`）の引数として依存オブジェクトを渡す方法です。

```python
# アプリケーションの起動時など、最も外側のレイヤーで実行される

# 1. 「詳細」のインスタンスを作成
user_repository = UserRepositoryImpl()

# 2. 「上位モジュール」に「詳細」を注入(inject)する
get_user_use_case = GetUserUseCase(repository=user_repository)

# 3. ユースケースを実行
user = get_user_use_case.execute("123")
```

これにより、`GetUserUseCase` のコードを変更することなく、依存するオブジェクトを `UserRepositoryImpl` からテスト用の `MockUserRepository` などに簡単に入れ替えることができます。

#### DIコンテナライブラリの活用

アプリケーションが大きくなると、手動でのDIは煩雑になります。そこで、依存関係の解決を自動的に行ってくれる **DIコンテナ** と呼ばれるライブラリが役立ちます。

Pythonでは `dependency-injector` が有名です。

```python
# container.py
from dependency_injector import containers, providers

# ユースケースやリポジトリのインポート
from .usecases import GetUserUseCase, IUserRepository
from .repositories import UserRepositoryImpl

class Container(containers.DeclarativeContainer):
    # 設定（シングルトン）
    config = providers.Configuration()

    # リポジトリの定義（シングルトン）
    user_repository: providers.Provider[IUserRepository] = providers.Singleton(
        UserRepositoryImpl
    )

    # ユースケースの定義（ファクトリ）
    get_user_use_case: providers.Provider[GetUserUseCase] = providers.Factory(
        GetUserUseCase,
        repository=user_repository,
    )

# main.py
from .container import Container

container = Container()

# DIコンテナからユースケースのインスタンスを取得
get_user_use_case = container.get_user_use_case()
user = get_user_use_case.execute("123")
```

DIコンテナを使うことで、依存関係の定義を一箇所に集約でき、管理が容易になります。

## 3-3. 推奨されるプロジェクト構成（ディレクトリ構造）

クリーンアーキテクチャのレイヤー構造を、実際のディレクトリ構造にマッピングする方法はいくつかありますが、以下に典型的で分かりやすい例を示します。

```
src/
├── domain/
│   ├── __init__.py
│   └── entities.py         # (Entities)
├── application/
│   ├── __init__.py
│   ├── use_cases.py        # (Use Cases / Interactors)
│   └── repositories.py     # (Repository Interfaces / Ports)
├── infrastructure/
│   ├── __init__.py
│   ├── database/
│   │   └── repositories.py # (Repository Implementations)
│   └── web/
│       ├── __init__.py
│       ├── controllers.py    # (Controllers)
│       └── presenters.py     # (Presenters)
└── main.py                 # (Frameworks & Drivers / DIコンテナの初期化)
```

*   `domain`: エンティティ層。プロジェクトの核となる部分。
*   `application`: ユースケース層。`domain` にのみ依存。
*   `infrastructure`: インターフェースアダプター層とフレームワーク層の一部。`application` に依存。
*   `main.py`: アプリケーションのエントリーポイント。すべてを結合する。

この構造により、ディレクトリ間の依存関係が、クリーンアーキテクチャの依存性のルールと一致し、見通しが良くなります。

## 3-4. データ形式の変換: DTO (Data Transfer Object) の役割

レイヤー間、特にアプリケーションの境界を越えてデータをやり取りする際には、**DTO (Data Transfer Object)** を使うのが一般的です。

DTOは、単にデータを保持・転送するためだけのオブジェクトで、ビジネスロジックを持ちません。

**なぜDTOが必要か？**

1.  **関心の分離**: Webフレームワークが受け取るリクエストの形式や、データベースのテーブル構造といった「詳細」を、ユースケース層やエンティティ層に持ち込みたくありません。DTOを中間のデータ形式として使うことで、この分離を保ちます。
2.  **堅牢性**: エンティティを直接APIのレスポンスとして返すと、意図しないプロパティ（例：パスワードハッシュ）を外部に公開してしまう危険性があります。DTOに必要なデータだけを詰めることで、安全性が高まります。

**例: Controller → UseCase**

```python
# --- infrastructure/web/controllers.py ---

# FastAPIがリクエストボディをPydanticモデルに変換
class CreateUserRequest(BaseModel):
    name: str
    email: str

@router.post("/users")
def create_user(req: CreateUserRequest):
    # DTO (Use Case Input) に変換
    input_data = CreateUserInput(name=req.name, email=req.email)
    use_case.execute(input_data)
    ...
```

このように、各レイヤーは自分たちの世界で最も扱いやすいデータ形式を使い、境界でDTOを介して変換を行うことで、それぞれの独立性を保つのです。
