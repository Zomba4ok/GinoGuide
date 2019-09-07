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
    owner = db.Column(None, db.ForeignKey('users.id'))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger(), autoincrement=True, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())


class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())


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

if __name__ == '__main__':
    app.run(debug=True, port=9009)
