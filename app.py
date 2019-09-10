# ---Sanic---
from sanic import Sanic
from sanic.response import json, html
# ---DB initialisation---
from gino.ext.sanic import Gino
# ---Creating engine---
import gino, sqlalchemy
from gino.schema import GinoSchemaVisitor
from sqlalchemy import Table, Column, Integer, String, MetaData
# ---Additional---
import time
import asyncio

app = Sanic()  # Sanic
app.config.from_pyfile('./config.py')  # Set db settings for Sanic
db = Gino()  # Create Gino object
db.init_app(app)


# ---Schema declaration---
class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.BigInteger(), autoincrement=True, primary_key=True)
    car_brand = db.Column(db.String())
    body_type = db.Column(db.String())
    owner = db.Column(Integer, db.ForeignKey('users.id'))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger(), autoincrement=True, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())


class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())


async def get_cars_list_with_delay(delay, conn):
    await asyncio.sleep(delay)
    cars = await conn.all('SELECT * FROM cars')
    return cars


async def get_car_owner_with_delay(delay, car):
    await asyncio.sleep(delay)
    query = db.select([User]).where(User.id == car.owner).execution_options(loader=User)
    owner = await query.gino.first()
    return owner


@app.route('/')
async def get_car(request):
    engine = await gino.create_engine('postgres://postgres:admin@localhost/postgres')
    async with engine.acquire() as conn:
        car = await conn.first('SELECT * FROM cars where car_brand = \'ferrari\'')

        start_time = time.time()
        tasks = [get_cars_list_with_delay(3, conn), get_car_owner_with_delay(2, car)]
        done, pending = await asyncio.wait(tasks)
        end_time = time.time()

    time_delta = end_time - start_time
    for item in done:
        if not type(item.result()) is list:
            owner = item.result()
    output = 'Car owner is {}. Query duration is {}'.format(owner.first_name + ' ' + owner.last_name, time_delta)
    return html(output)


if __name__ == '__main__':
    app.run(debug=True, port=9009)
