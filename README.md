# Введение 

Gino - легковесный асинхронный ORM построенный на ядре SQLAlchemy для библиотеки Python asyncio.

На данный момент Gino поддерживает только один диалект - asyncpg.

Gino позволяет писать и выполнять низкоуровыневые SQL запросы из API в БД асинхронно. 

# Установка

Установка самого Gino производится с помощью файлового менеджера pip.
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
Помимо сторонних библиотек (например, [alembic](https://pypi.org/project/alembic/)) для миграции схемы в базу можно также применить встроенную функцию `create_all()`. Для ее работы необходимо объявить `engine`. Это действие будет рассмотрено ниже в пункте **Создание engine**.
```
import gino
from gino.schema import GinoSchemaVisitor

async def main():
    engine = await gino.create_engine('postgresql://...')
    await GinoSchemaVisitor(metadata).create_all(engine)
```
Синтаксис и принципы работы взяты из [SQLAlchemy core](https://docs.sqlalchemy.org/en/13/core/metadata.html).

### Gino core

В первую очередь создается объект Gino (обычно, его называют **db**):
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

**Обратите внимание, что переменная `target_metadata` объявлена в файле изначально, вам нужно только изменить ее значение.**
 
 Теперь для применения миграций вам достаточно ввести две команды.
 
 Для автогенерации миграций на основе созданных моделей:
 ```
 alembic revision -m "Migration message" --autogenerate --head head
 ```
 И для их применения:
 ```
 alembic upgrade head
 ```

# Engine

ля создания **engine** Gino предоставляет метод `gino.create_engine()`. Он полностью повторяет поведение аналогичного метода в SQLAchemy за исключением установленного по умолчанию параметра `strategy = 'gino'.
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

Как только подключение создано, можно приступать непосредственно к написанию SQL запросов. В Gino существует 4 разных метода для их выполнения: `all()`, `first()`, `scalar()`, `status()`. Все они работают одинаково, но отличаются возвращаемыми значениями. 

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

`scalar()` удобен для выполнения таких функций как MIN(), MAX(), COUNT() и др.

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


Никогда нельзя точно сказать, сколько времени займет await, при чем слишком долгое удержание транзакций может привести к серьезным сбоям в работе приложения. Gino решает эту проблему, путем обеспечения явного управления транзакциями.

Обычно, транзакция в Gino инициализируется следующим образом:
```
async with connection.transaction() as tx:
    await connection.all( ...
```
Но иногда транзакция также инициализируется на экземпляре Gino или GinoEngine.

Для управления транзакциями Gino также предоставляет два метода: `tx.raise_commit()` и `tx.raise_rollback()`. Закрытие происходит автоматически при выходе из блока.

При необходимости, все транзакции в Gino можно контролировать вручную:
```
tx = await connection.transaction()
try:
    await db.status(...
    await tx.commit()
except Exception:
    await tx.rollback()
    raise
```

# Загрузчики

### Model loader

Загрузчик **Model loader** позволяет получать строки базы данных в виде объектов, а не списков, как в случае с прямыми запросами.
```
@app.route('/')
async def get_car(request):
    query = db.select([Car])
    cars = await query.gino.all()
    return html(cars)
```
Результатом выполнения данного когда станет список кортежей - строк из БД.

![5](https://user-images.githubusercontent.com/49648818/64342034-57961680-cff2-11e9-8b64-1059f69b0082.jpg)

Теперь установим в запросе загрузку данных с помощью **Model loader**:
```
from gino.loader import ModelLoader

class Car(db.Model):
#...

@app.route('/')
async def get_car(request):
    # engine = await gino.create_engine('postgres://postgres:admin@localhost/postgres')
    # async with engine.acquire() as conn:
    query = db.select([Car])
    query = query.execution_options(loader=Car)
    cars = await query.gino.all()
    return html(cars)
```
И снова выполним метод:

![6](https://user-images.githubusercontent.com/49648818/64342317-ec990f80-cff2-11e9-97c8-b2e82ee8d262.png)

Использование model_loader не ускоряет работы API, но делает код более понятным и удобным, за счет обращения к данным через свойства объектов.

### Создание загрузчиков

**Model loader** далеко не единственный загрузчик, предоставляемый Gino. Существую и другие загрузчики изменяющие вывод строк БД. Они подключаются следующим образом:
```
from gino.loader import ColumnLoader

query = db.select([User]).execution_options(loader=ColumnLoader(User))
```
Под капотом все загрузички являются процессрами строк. При необходимости можно настроить и свой собственный загрузчик:
```
@app.route('/')
async def get_car(request):
    # engine = await gino.create_engine('postgres://postgres:admin@localhost/postgres')
    # async with engine.acquire() as conn:
    query = db.select([Car]).gino.load(
        (
            Car.id,
            Car,
            lambda row, ctx: len(row)
        )
    )
    cars = await query.first()
    return html(cars)
```

![7](https://user-images.githubusercontent.com/49648818/64349342-7058f900-cfff-11e9-91e1-2449e625ca30.png)

### Many-To-One relationship

Gino не поддерживает автоматического свзяывания таблиц, вместо этого разработчику предлагается использовать загрузчики для ручного управления связями таблиц.
```
@app.route('/')
    owners = []
    async with db.transaction():
        async for car in Car.load(parent=User).gino.iterate():
            owners.append(car.parent)
    return html(owners)

```
Результатом выполнения приведенного выше метода будет список объектов класса User, указанных в классе Car c помощью Foreign Key.

![image](https://user-images.githubusercontent.com/49648818/64427014-cdfd4c00-d0b8-11e9-8061-922c81011caf.png)

Загрузчик load добавляет объект родительского класса в объект дочернего перед тем, как вернуть его. Это позволяет обращаться к родителю объекта и позже, например так:
```
@app.route('/')
async def get_car(request):
    cars = []
    async with db.transaction():
        async for car in Car.load(parent=User).gino.iterate():
            cars.append(car)
    return html(cars[0].parent)
```

![image](https://user-images.githubusercontent.com/49648818/64427000-c2aa2080-d0b8-11e9-9d4c-bdea9a0d04c5.png)

# Примеры работы с Gino

```
async def query():
    engine = await gino.create_engine('postgres://postgres:admin@localhost/postgres')
    async with engine.acquire() as conn:
        objects = await conn.all('SELECT * FROM cars')
    return objects
    
    
@app.route('/')
async def get_car(request):
    start_time = time.time()
    tasks = [query() for i in range(1, 5)]
    await asyncio.wait(tasks)
    end_time = time.time()
    return html(end_time - start_time)
```

![image](https://user-images.githubusercontent.com/49648818/64472239-e2e2e980-d163-11e9-88fd-da037e50bf0e.png)




***P.S.
Как говорилось ранее, Gino написано на основе SQLAlchemy и большУю часть функционала наследует из данной ORM. Не забывайте об этом при работе с Gino***
