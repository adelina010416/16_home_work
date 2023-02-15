import datetime
import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.url_map.strict_slashes = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)

    def make_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    # order = db.relationship("Order")
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def make_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def make_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


def default(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()


with app.app_context():
    db.create_all()

    users = [User(**user) for user in data.users]
    db.session.add_all(users)
    db.session.commit()

    offers = [Offer(**offer) for offer in data.offers]
    db.session.add_all(offers)
    db.session.commit()

    for order in data.orders:
        order["start_date"] = datetime.datetime.strptime(order["start_date"], "%m/%d/%Y").date()
        order["end_date"] = datetime.datetime.strptime(order["end_date"], "%m/%d/%Y").date()
        db.session.add(Order(**order))
        db.session.commit()


@app.route("/users", methods=['GET', 'POST'])
def all_users_page():
    result = []
    if request.method == 'GET':
        all_users = User.query.all()
        [result.append(user.make_dict()) for user in all_users]
        return json.dumps(result, sort_keys=False, indent=4), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        new_data = json.loads(request.data)
        db.session.add(User(**new_data))
        db.session.commit()
        return "", 201


@app.route("/users/<int:user_id>", methods=['GET', 'PUT', 'DELETE'])
def user_by_id(user_id):
    user = User.query.get(user_id)
    if request.method == 'GET':
        return json.dumps(user.make_dict(), sort_keys=False, indent=4), \
            200, {'Content-Type': 'application/json; charset=utf-8'}

    elif request.method == 'PUT':
        new_data = json.loads(request.data)

        user.first_name = new_data['first_name']
        user.last_name = new_data['last_name']
        user.age = new_data['age']
        user.email = new_data['email']
        user.role = new_data['role']
        user.phone = new_data['phone']

        db.session.add(user)
        db.session.commit()
        return "", 201

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return "", 201


@app.route("/orders", methods=['GET', 'POST'])
def all_orders_page():
    result = []
    if request.method == 'GET':
        all_orders = Order.query.all()
        [result.append(odr.make_dict()) for odr in all_orders]
        return json.dumps(result, default=default, ensure_ascii=False, sort_keys=False, indent=4), \
            200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        new_data = json.loads(request.data)
        db.session.add(Order(**new_data))
        db.session.commit()
        return "", 201


@app.route("/orders/<int:order_id>", methods=['GET', 'PUT', 'DELETE'])
def order_by_id(order_id):
    order = Order.query.get(order_id)
    if request.method == 'GET':
        return json.dumps(order.make_dict(), default=default, ensure_ascii=False, sort_keys=False, indent=4), \
            200, {'Content-Type': 'application/json; charset=utf-8'}

    elif request.method == 'PUT':
        new_data = json.loads(request.data)

        order.name = new_data['name']
        order.description = new_data['description']
        order.start_date = new_data['start_date']
        order.end_date = new_data['end_date']
        order.address = new_data['address']
        order.price = new_data['price']
        order.customer_id = new_data['customer_id']
        order.executor_id = new_data['executor_id']

        db.session.add(order)
        db.session.commit()
        return "", 201

    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return "", 201


@app.route("/offers", methods=['GET', 'POST'])
def all_offers_page():
    result = []
    if request.method == 'GET':
        all_offers = Offer.query.all()
        [result.append(offer.make_dict()) for offer in all_offers]
        return json.dumps(result, ensure_ascii=False, sort_keys=False, indent=4), \
            200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        new_data = json.loads(request.data)
        db.session.add(Offer(**new_data))
        db.session.commit()
        return "", 201


@app.route("/offers/<int:offer_id>", methods=['GET', 'PUT', 'DELETE'])
def offer_by_id(offer_id):
    offer = Offer.query.get(offer_id)
    if request.method == 'GET':
        return json.dumps(offer.make_dict(), ensure_ascii=False, sort_keys=False, indent=4), \
            200, {'Content-Type': 'application/json; charset=utf-8'}

    elif request.method == 'PUT':
        new_data = json.loads(request.data)

        offer.order_id = new_data['order_id']
        offer.executor_id = new_data['executor_id']

        db.session.add(offer)
        db.session.commit()
        return "", 201

    elif request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return "", 201


if __name__ == '__main__':
    app.run(debug=True)
