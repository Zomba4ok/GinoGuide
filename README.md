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
Так же, по скольку Gino не поддерживает механизма миграция из коробки, необходимо использовать другие библиотеки для перенесения моделей в БД. Например [alembic](https://pypi.org/project/alembic/).
```
pip install alembic
```
**Не забывайте, что Gino будет корректно работать только для асинхронных web framework'ов, как, например, [Sanic](https://github.com/huge-success/sanic) или [Aiohttp](https://github.com/aio-libs/aiohttp)**

# Создание схемы БД

Существует 3 способа задания схемы БД. 

***Gino ORM***
Это классический способ задания схемы БД для многих web framework'ов.

В первую очередь необходмо создать объект Gino (обычно, его называют **db**):
```
db = Gino()
```
Далее создается непосредственно класс модели (в родителях класса указывается db.Model либо другой класс Gino модели):
```
class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.BigInteger(), autoincrement=True, primary_key=True)
    car_brand = db.Column(db.Unicode())
    body_type = db.Column(db.String())
```
Переменная `__tablename__`  определяет название соответствующей таблицы в БД.
Типы данных `db.BigInteger()`, `db.Unicode()`, полностью аналогичны [Generic types](https://docs.sqlalchemy.org/en/13/core/type_basics.html) SQLAlchemy

***Gino engine***
Удобен, когда необходимо добавить в уже написанный на SQLAlchemy код поддержку асинхронной работы.
```
metadata = MetaData()

owners = Table(
    'owners', metadata,

    Column('id', Integer, primary_key=True),
    Column('first name', String),
    Column('last name', String)
)
```
Помимо сторонних библиотек ([alembic](https://pypi.org/project/alembic/)) для миграции схемы в базу можно также применить встроенную функцию `create_all()`. Для ее работы также необходимо объявить `engine`. Это действие будет рассмотрено ниже:
```
import gino
from gino.schema import GinoSchemaVisitor

async def main():
    engine = await gino.create_engine('postgresql://...')
    await GinoSchemaVisitor(metadata).create_all(engine)
```
Синтаксис и принципы работы взят из [SQLAlchemy core](https://docs.sqlalchemy.org/en/13/core/metadata.html).

***Gino core***
Как и в варианте **Gino ORM** необходимо создать объект Gino:
```
db = Gino()
```
