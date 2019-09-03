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
Так же, по скольку Gino не поддерживает механизма миграция из коробки, необходимо использовать другие библиотеки для перенесения моделей в БД. Например alembic.
```
pip install alembic
```
**Не забывайте, что Gino будет корректно работать только для асинхронных web framework'ов, как, например, [Sanic](https://github.com/huge-success/sanic) или [Aiohttp](https://github.com/aio-libs/aiohttp)**

# Создание моделей

