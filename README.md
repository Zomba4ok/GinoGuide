# Введение 

Gino - легковесный асинхронный ORM построенный на ядре SQLAlchemy для библиотеки Python asyncio.

На данный момент Gino поддерживает только один диалект - asyncpg.

Gino позволяет писать и выполнять низкоуровыневые SQL запросы из API в БД асинхронно. 

# Установка

Установка самого Ginoпроизводится с помощью файлового менеджера pip.
```
pip install gino
```
**Не забывайте, что Gino будет корректно работать только для асинхронных web framework'ов, как, например, [Sanic](https://github.com/huge-success/sanic) или [Aiohttp](https://github.com/aio-libs/aiohttp)**

# Создание схемы БД

Существует 3 способа задания схемы БД. 

### Gino engine

Удобен, когда необходимо добавить в уже написанный на SQLAlchemy код поддержку асинхронной работы.
```
from sqlalchemy import Table, Column, Integer, String, MetaData

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

### Gino core

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
### Gino ORM

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

Все доступные способы миграции аналогичны таковым в **Gino core**.

# Миграции с alembic

Библиотека [alembic](https://pypi.org/project/alembic/) позволяет настроить применение миграция к базе по команде из консоли. Для этого необходимо выполнить следующие шаги:

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
Здесь мы импортируем metadata (это будет объект Gino или metadata SQLAlchemy в зависимости от способа задания схемы БД) и присваиваем его `target_metadata`.

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

# Создание engine

Как и в случае с схемами БД есьт несколько способов объявления engine: с помощью функции ядра SQLAlchemy `create_all()` и с помощью аналогичной функции ядра Gino.

### SQLAlchemy core

В данном случае engine объявляется также, как и для SQLalchemy, но с параметром `stratagy = 'gino'`.
```
import gino

async def main():
    engine = await gino.create_engine('postgres://{{username}}:{{password}}@{{address}}/{{db_name}}')
```
**Обратите внимания, что без `import gino` функция работать не будет**

### Gino core

Функция `gino.create_engine()` ничем не отличается от `sqlalchemy.create_engine()`,за исключением установленного по умолчанию параметра `stratagy = 'gino'.
```
import gino

async def main():
    engine = await gino.create_engine('postgres://{{username}}:{{password}}@{{address}}/{{db_name}}')
```

# Connections

Для создания подключения в gino используется метод `engine.acquire()`:
```
connection = await engine.acquire()
```
После выполнения всех операция соединение необходимо закрывать:
```
await connection.release()
```
Функция `acquire` также способна принимать несколько keyword аргументов (reuse, lazy и reusable).

# SQL запросы

Как только подключение создано, можно приступать непосредственно к написанию SQL запросов. В Gino существует 4 разных методы для их (запросов) выполнения: `all()`, `first()`, `scalar()`, `status()`. Все они работают одинаково, но отличаются возвращаемыми значениями. 

### all()

Метод `all()` всегда возвращает список. Он может быть пустым, если у запроса нет результата, но это все равно будет список.
```
@app.route('/')
async def get_car(request):
    engine = await gino.create_engine('postgres://postgres:admin@localhost/postgres')
    async with engine.acquire() as conn:
        cars = await conn.all('SELECT * FROM cars')
    return html(cars)
```
Результат выполнения данного метода показан на рисунке ниже.

![1](https://user-images.githubusercontent.com/49648818/64254255-b04cad00-cf27-11e9-9ee1-349d6e9e2b27.jpg)

В случае, когда запрос не возвращает ничего (например `ISNERT`), all() возвращает пустой список. 

После замены sql запроса `SELECT` в коде приведенной выше функции на `INSERT INTO cars (car_brand, body_type, owner) VALUES(\'skoda\', \'sedan\', 1)`,  мы полчили следующий вывод:

![2](https://user-images.githubusercontent.com/49648818/64258071-37e9ea00-cf2f-11e9-8d59-33a25ffa4359.jpg)

### first()

`first()` возвращает первый результат запроса или none, если результата нет. 

Выполнение запроса `SELECT * FROM table_name` приведет к выводу только первой строки, как в примере ниже.
```
@app.route('/')
async def get_car(request):
    engine = await gino.create_engine('postgres://postgres:admin@localhost/postgres') 
    async with engine.acquire() as conn:
        cars = await conn.first('SELECT * FROM cars')
    return html(cars)
```

![3](https://user-images.githubusercontent.com/49648818/64258078-3a4c4400-cf2f-11e9-8dcd-da89e3fc98c6.jpg)

### scalar()

Этот метод также как и first возвращает первый результат или none, если результат нет. Но, в отличие от`first()` этот метод возвращает только скалярные величины (к примеру, вместо строки результата она вернет только ее primary key).

Этот метод удобен для выполнения, например, функций MIN(), MAX(), COUNT() и др.

### status()

Метод `status()` выполняет SQL запрос и возвращает кортеж из двух элементов: статуса выполнения запроса и результата его выполнения.

```
@app.route('/')
async def get_car(request):
    engine = await gino.create_engine('postgres://postgres:admin@localhost/postgres') 
    async with engine.acquire() as conn:
        cars = await conn.status('SELECT * FROM cars WHERE owner=1')
    return html(cars)

```

![4](https://user-images.githubusercontent.com/49648818/64258497-0c1b3400-cf30-11e9-8d1a-92b4ae9e4398.jpg)


# Транзакции


Никогда невозможно точно сказать, сколько времени займет await, при чем слишком долгое удержание транзакций может привести к серьезным сбоям в работе приложения. Gino решает эту проблему, путем обеспечения явного управления транзакциями.

Обычно, транзакция в Gino инициализируется следующим образом:
```
async with connection.transaction() as tx:
    await connection.all( ...
```
Но иногда транзакция также инициализируется на экземпляре Gino или GinoEngine.

Для управления транзакциями Gino также предоставляет два метода: `tx.raise_commit()` и `tx.raise_rollback()`. Закрытие происходит автоматически при выходе из блока.

При необходимости все транзакции в Gino можно контролировать вручную:
```
tx = await connection.transaction()
try:
    await db.status(...
    await tx.commit()
except Exception:
    await tx.rollback()
    raise
```

