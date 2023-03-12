import json
#Импортирую необходимые модули
from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from utils import load_from_json, formated_response

#Создаю объект flask
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.bd"
db = SQLAlchemy(app)

#Задаю параметры таблиц

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)

    def to_dict(self):
        return {"id": self.id,
         "first_name": self.first_name,
         "last_name": self.last_name,
         "age": self.age,
         "email": self.email,
         "role": self.role,
         "phone": self.phone}

    db.relationship("Offer")
    db.relationship("Order")


class Offer(db.Model):
    __tablename__ = "offer"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {"id": self.id,
        "order_id": self.order_id,
        "executor_id": self.executor_id}



class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {"id": self.id,
         "name": self.name,
         "description": self.description,
         "start_date": self.start_date,
         "end_date": self.end_date,
         "address": self.address,
         "price": self.price,
         "customer_id": self.customer_id,
         "executor_id": self.executor_id}

#Получаю необходимые данные

users = load_from_json('users.json')
orders = load_from_json('orders.json')
offers = load_from_json('offers.json')

#Записываю данные и создаю объекты


with app.app_context():
    db.drop_all()
    db.create_all()

    for user in users:
        new_user = User(**user)
        db.session.add(new_user)
        db.session.commit()

    for order in orders:
        incorrect_form_stdate = order["start_date"]
        order["start_date"] = datetime.strptime(incorrect_form_stdate, "%m/%d/%Y").date()
        incorrect_form_enddate = order["end_date"]
        order["end_date"] = datetime.strptime(incorrect_form_enddate, "%m/%d/%Y").date()
        new_order = Order(**order)
        db.session.add(new_order)
        db.session.commit()

    for offer in offers:
        new_offer = Offer(**offer)
        db.session.add(new_offer)
        db.session.commit()


@app.route("/users", methods=["GET", "POST"])
def get_all_users():
    if request.method == "GET":
        users = User.query.all()
        users_list = []
        for user in users:
            users_list.append(user.to_dict())
        return formated_response(users_list)

    elif request.method == "POST":
        new_user = json.loads(request.data)
        print(new_user)
        db.session.add(User(**new_user))
        db.session.commit()
        return f"Пользователь {new_user['first_name']} {new_user['last_name']} добавлен", 201

@app.route("/users/<int:id>", methods=["GET", "PUT","DELETE"])
def get_user_by_id(id):
    if request.method == "GET":
        user_row = User.query.get(id)
        user = user_row.to_dict()
        return formated_response(user)

    elif request.method == "PUT":
        user = User.query.get(id)
        updated_info = json.loads(request.data)
        user.first_name = updated_info["first_name"]
        user.last_name = updated_info["last_name"]
        user.age = updated_info["age"]
        user.role = updated_info["role"]
        user.email = updated_info["email"]
        user.phone = updated_info["phone"]
        db.session.add(user)
        db.session.commit()
        return f"Данные пользователя {user.first_name} {user.last_name} обновлены"

    elif request.method == "DELETE":
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return f"Пользователь {user.first_name} {user.last_name} удален"

@app.route("/orders", methods=["GET", "POST"])
def get_all_orders():
    if request.method == "GET":
        orders = Order.query.all()
        orders_list = []
        for order in orders:
            orders_list.append(order.to_dict())
        return jsonify(orders_list)

    elif request.method == "POST":
        new_order = json.loads(request.data)
        incorrect_form_stdate = new_order["start_date"]
        new_order['start_date'] = datetime.strptime(incorrect_form_stdate, "%m/%d/%Y").date()
        incorrect_form_enddate = new_order["end_date"]
        new_order['end_date'] = datetime.strptime(incorrect_form_enddate, "%m/%d/%Y").date()
        db.session.add(Order(**new_order))
        db.session.commit()
        return f"Заказ '{new_order['name']}' создан"


@app.route("/orders/<int:id>", methods=["GET", "PUT", "DELETE"])
def get_order_by_id(id):
    if request.method == "GET":
        order_raw = Order.query.get(id)
        order = order_raw.to_dict()
        return jsonify(order)


    elif request.method == "DELETE":
        order = Order.query.get(id)
        db.session.delete(order)
        db.session.commit()
        return f"Заказ #{order.id} удален"

    elif request.method == "PUT":
        order = Order.query.get(id)
        updated_info = json.loads(request.data)
        order.executor_id = updated_info["executor_id"]
        order.customer_id = updated_info["customer_id"]
        order.price = updated_info["price"]
        incorrect_form_stdate = updated_info["start_date"]
        order.start_date = datetime.strptime(incorrect_form_stdate, "%m/%d/%Y").date()
        incorrect_form_enddate = updated_info["end_date"]
        order.end_date = datetime.strptime(incorrect_form_enddate, "%m/%d/%Y").date()
        order.name = updated_info["name"]
        order.description = updated_info["description"]
        order.address = updated_info["address"]
        db.session.add(order)
        db.session.commit()
        return f"Данные заказа #{order.id} {order.name} обновлены"

@app.route("/offers", methods=["GET", "POST"])
def get_all_offers():
    if request.method == "GET":
        offers_list = []
        offers = Offer.query.all()

        for offer in offers:
            offers_list.append(offer.to_dict())
        return formated_response(offers_list)

    elif request.method == "POST":
        new_offer = json.loads(request.data)
        print(new_offer)
        db.session.add(Offer(**new_offer))
        db.session.commit()
        return f"Предложение о выполнении заказа #{new_offer['id']} добавлено"

@app.route("/offers/<int:id>", methods=["GET", "PUT", "DELETE"])
def get_offer_by_id(id):
    if request.method == "GET":
        offer_raw = Offer.query.get(id)
        offer = {"id": offer_raw.id,
                 "order_id": offer_raw.order_id,
                 "executor_id": offer_raw.executor_id}
        return formated_response(offer)

    elif request.method == "DELETE":
        offer = Offer.query.get(id)
        db.session.delete(offer)
        db.session.commit()
        return f"Предложение о выполнении заказа #{offer.id} удалено"

    elif request.method == "PUT":
        offer = Offer.query.get(id)
        updated_info = json.loads(request.data)
        offer.order_id = updated_info["order_id"]
        offer.executor_id = updated_info["executor_id"]
        db.session.add(offer)
        db.session.commit()
        return f"Предложение о выполнении заказа #{offer.id} обновлено"



if __name__ == '__main__':
    app.run(debug=True)