import random

import databases
import sqlalchemy
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from faker import Faker
from datetime import date


app = FastAPI()

DATABASE_URL = "sqlite:///my_database.db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("product_name", sqlalchemy.String(32)),
    sqlalchemy.Column("description", sqlalchemy.String(1280)),
    sqlalchemy.Column("price", sqlalchemy.Float(10))
)

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("firstname", sqlalchemy.String(32)),
    sqlalchemy.Column("lastname", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("passw", sqlalchemy.String(32))
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_user", sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column("id_product", sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column("date_order", sqlalchemy.String(26)),
    sqlalchemy.Column("status", sqlalchemy.String(128))
)

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False})
metadata.create_all(engine)


class ProductIn(BaseModel):
    product_name: str = Field(max_length=32)
    description: str = Field(max_length=1280)
    price: float = Field(max_length=128)

class Product(ProductIn):
    id: int


class UserIn(BaseModel):
    firstname: str = Field(max_length=32)
    lastname: str = Field(max_length=32)
    email: str = Field(max_length=128)
    passw: str = Field(max_length=32)


class User(UserIn):
    id: int


class OrderIn(BaseModel):
    id_user: int
    id_product: int
    date_order: str = Field(max_length=10)
    status: str = Field(max_length=128)


class Order(OrderIn):
    id: int


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# @app.get("/fake_data/{count}")
# async def create_note(count: int):
#     """
#     создание фейковых данных для проверки работы ДБ
#     """
#     name_prod = ['яблоки', 'груши', 'шоколад']
#     orders_status = ['paid', 'for assembly', 'delivery', 'delivered']
#     for i in range(len(name_prod)):
#         query = products.insert().values(product_name=name_prod[i], description="вкусный товар", price=10.0)
#         await database.execute(query)
#     for i in range(count * 10):
#         faker = Faker()
#         name = faker.name()
#         name_list = name.split()
#         query = users.insert().values(firstname=name_list[0], lastname=name_list[1],
#                                       email=Faker().email(), passw=faker.password())
#         await database.execute(query)
#     for i in range(count * 2):
#         query = orders.insert().values(id_user=random.randint(1, (count * 10)),
#                                        id_product=random.randint(1, len(name_prod)),
#                                        date_order=date.today(),
#                                        status=orders_status[random.randint(0, len(orders_status)-1)])
#         await database.execute(query)
#     return {'message': f'Fake data create'}

@app.get("/products/", response_model=list[User])
async def read_products():
    """
    получение списка всех товаров
    """
    query =products.select()
    return await database.fetch_all(query)


@app.get("/users/", response_model=list[User])
async def read_users():
    """
    получение списка всех пользователей
    """
    query =users.select()
    return await database.fetch_all(query)


@app.get("/orders/", response_model=list[User])
async def read_orders():
    """
    получение списка всех заказов
    """
    query =orders.select()
    return await database.fetch_all(query)


@app.post("/product/", response_model=Product)
async def crate_product(product: ProductIn):
    """
    добавление нового продукта
    """
    query = products.insert().values(**product.dict())
    last_record_id = await database.execute(query)
    return {**product.dict(), 'id': last_record_id}


@app.post("/user/", response_model=User)
async def crate_user(user: UserIn):
    """
    добавление нового пользователя
    """
    query = users.insert().values(**user.dict())
    last_record_id = await database.execute(query)
    return {**user.dict(), 'id': last_record_id}


@app.post("/order/", response_model=Order)
async def crate_order(order: OrderIn):
    """
    добавление нового заказа
    """
    query = orders.insert().values(**order.dict())
    last_record_id = await database.execute(query)
    return {**order.dict(), 'id': last_record_id}


@app.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int):
    """
    получение данных о товаре
    """
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    """
    получение данных о пользователе
    """
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int):
    """
    получение данных о заказе
    """
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.put("/product/{product_id}", response_model=Product)
async def update_product(product_id: int, new_poduct: ProductIn):
    """
    обновление данных о продукте
    """
    query = products.update().where(products.c.id == product_id).values(**new_poduct.dict())
    await database.execute(query)
    return {**new_poduct.dict(), "id": product_id}


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    """
    добавление данных о пользователе
    """
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
    """
    добавление данных о заказе
    """
    query = orders.update().where(orders.c.id == order_id).values(**new_order.dict())
    await database.execute(query)
    return {**new_order.dict(), "id": order_id}


@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """
    удаление продукта
    """
    query = orders.select().where(orders.c.id_product == product_id)
    if query is None or query.get('status') == 'delivered':
        query = products.delete().where(products.c.id == product_id)
        await database.execute(query)
        return {'message': 'Product deleted'}
    else:
        return {'message': 'The product has not been deleted, there is an undelivered order'}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """
    удаление пользователя
    """
    query = orders.select().where(orders.c.id_user == user_id)
    if query is None:
        query = users.delete().where(users.c.id == user_id)
        await database.execute(query)
        return {'message': 'User deleted'}
    else:
        return {'message': 'The user has not been deleted, there are records of orders'}


@app.delete("/orders/{order_id}")
async def delete_order(order_id:int):
    """
    удаление заказа
    """
    query = users.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': 'Order deleted'}
