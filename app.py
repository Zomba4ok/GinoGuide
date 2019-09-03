# Sanic
from sanic import Sanic
from sanic.exceptions import abort
from sanic.response import json

# DB initialisation
from gino.ext.sanic import Gino

# Creating engine
import gino, sqlalchemy

app = Sanic()  # Sanic
app.config.from_pyfile('./config.py')  # Set db settings
db = Gino()  #
db.init_app(app)  #


class Car(db.Model):  # Create model
    __tablename__ = 'cars'
    id = db.Column(db.BigInteger(), autoincrement=True, primary_key=True)
    car_brand = db.Column(db.Unicode())
    body_type = db.Column(db.String())


@app.route('/')
async def get_car(request):
    gino_engine = await gino.create_engine('postgres://postgres:admin@localhost/postgres')  # engine creating
    # gino_engine = await sqlalchemy.create_engine('postgres://postgres:admin@localhost/postgres', strategy='gino')
    async with gino_engine.acquire() as conn:
        car = await conn.status('SELECT * FROM cars')
    return json({'name': car})


if __name__ == '__main__':
    app.run(debug=True)
