# Введение 

Согласно введению, в официальном git репозитории Gino: 

*GINO - GINO Is Not ORM - is a lightweight asynchronous ORM built on top of SQLAlchemy core for Python asyncio. Now (early 2018) GINO supports only one dialect asyncpg.*

Говоря простым языком, Gino позволяет писать и выполнять низкоуровыневые SQL запросы из API в БД асинхронно. 

Создатели библиотеки так же отмечают, что Gino не является ORM. 

*The Objects in GINO are completely stateless from database - they are pure plain Python objects in memory. Changing their attribute values does not make them "dirty" - or in a different way of thinking they are always "dirty". Any access to database must be explicitly executed. Using GINO is more like making up SQL clauses with Models and Objects, executing them to make changes in database, or loading data from database and wrapping the results with Objects again. Objects are just row data containers, you are still dealing with SQL which is represented by Models and SQLAlchemy core grammars.*

# Установка

Установка самого Gino.
```
pip install gino
```
**Не забывайте, что Gino будет корректно работать только для асинхронных web framework'ов, как, например, [Sanic](https://github.com/huge-success/sanic) или [Aiohttp](https://github.com/aio-libs/aiohttp)**

# Создание схемы БД

Существует 3 способа задания схемы БД. 

***Gino engine***

Удобен, когда необходимо добавить в уже написанный на SQLAlchemy код поддержку асинхронной работы.
```
metadata = MetaData()

users = Table(
    'users', metadata,

    Column('id', Integer, primary_key=True),
    Column('first_name', String),
    Column('last_name', String)
)
```
Помимо сторонних библиотек (например, [alembic](https://pypi.org/project/alembic/)) для миграции схемы в базу можно также применить встроенную функцию `create_all()`. Для ее работы также необходимо объявить `engine`. Это действие будет рассмотрено ниже в пункте **Создание engine**.
```
import gino
from gino.schema import GinoSchemaVisitor

async def main():
    engine = await gino.create_engine('postgresql://...')
    await GinoSchemaVisitor(metadata).create_all(engine)
```
Синтаксис и принципы работы взяты из [SQLAlchemy core](https://docs.sqlalchemy.org/en/13/core/metadata.html).

***Gino core***

В первую очередь необходимо создать объект Gino (обычно, его называют **db**):
```
db = Gino()
```
Дальнейшие действия аналогичны **Gino engine** за исключением используемого ядра (Gino core вместо SQLAlchemy core).
```
from gino import Gino

db = Gino()

users = db.Table(
    'users', db,

    db.Column('id', db.Integer, primary_key=True),
    db.Column('first_name', db.String),
    db.Column('last_name', db.String),
)
```
Миграции, как и в предыдущем случае можно провести с помощью [alembic](https://pypi.org/project/alembic/) или встроенной функции `create_all()`:
```
async with db.with_bind('postgresql://localhost/gino'):
    await db.gino.create_all()
```
***Gino ORM***

Это классический способ задания схемы БД для многих web framework'ов.

Как и в предыдущем случае создаем объект Gino:
```
db = Gino()
```
Далее создается непосредственно класс модели (в родителях класса указывается db.Model либо другой класс Gino модели):
```
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger(), autoincrement=True, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
```
Переменная `__tablename__`  определяет название соответствующей таблицы в БД.
Типы данных `db.BigInteger()`, `db.Unicode()`, полностью аналогичны [Generic types](https://docs.sqlalchemy.org/en/13/core/type_basics.html) SQLAlchemy

Все доступные способы миграции аналогичны таковым в **Gino ore**.

# Миграции с alembic

Библиотека [alembic](https://pypi.org/project/alembic/) позволяет настроить применение миграция к базе по команде из консоли. Для этого необходимо выполнить следующие шаги?

Установить библиотеку.
```
pip install alembic
```
Находясь в папке проекта выполнить в консоли bash:
```
alembic init alembic
```
Появившийся файл `alembic.ini` открыть любым текстовым редактором в строке `sqlachemy.url = ` ввести адрес сервера БД:
```
sqlalchemy.url = postgres://{{username}}:{{password}}@{{address}}/{{db_name}}
```
Далее перейти в появившуся после инициализации папку `alembic` в ней открыть файл `env.py` и добавить следующие строки:
```
from {{my_prject_dir}} import {{metadata}}

target_metadata = db
```
Здесь мы импортируем metadata (это будет объект Gino или SQLAlchemy в зависимости от способа задания схемы БД) и присваиваем его `target_metadata`.
**Обратите внимание, что переменная `target_metadata` объявлена в файле изначально, вам нужно только изменить ее значение.
 
 Теперь для применения миграций вам достаточно ввести две команды.
 
 Для автогенерации миграций на основе созданных моделей:
 ```
 alembic revision -m "Migration message" --autogenerate --head head
 ```
 И для их применения:
 ```
 alembic upgrade head
 ```
