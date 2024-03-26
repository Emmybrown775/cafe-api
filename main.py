import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record

@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    cafes_dict = []
    for cafe in cafes:
        cafe_dict = cafe_to_dict(cafe)
        cafes_dict.append(cafe_dict)
    return jsonify(cafes=cafes_dict)


@app.route("/search")
def search_cafes():
    location = request.args["loc"].title()
    cafe = Cafe.query.filter_by(location=location).first()
    if cafe is not None:
        print(cafe)
        cafe_dict = cafe_to_dict(cafe)
        return jsonify(cafe_dict)
    else:
        error = {
            "Not Found": "Sorry we don't have a cafe at that location"
        }
        return jsonify(error=error)


@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    rand_cafe = random.choice(cafes)
    cafe_dict = cafe_to_dict(rand_cafe)
    return jsonify(cafe_dict)


# HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def add_cafe():
    response = {
        "success": "added successfully"
    }
    data = request.form.to_dict()
    new_cafe = Cafe(
        name=data["name"],
        map_url=data["map_url"],
        img_url=data["img_url"],
        location=data["location"],
        seats=data["seats"],
        has_toilet=bool(data["has_toilet"]),
        has_wifi=bool(data["has_wifi"]),
        has_sockets=bool(data["has_sockets"]),
        can_take_calls=bool(data["can_take_calls"]),
        coffee_price=data["coffee_price"]
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response=response)

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update_price(id):
    response = {
        "success": "updated successfully"
    }
    price = request.args["new_price"]
    selected_cafe = Cafe.query.filter_by(id=id).first()
    if selected_cafe is not None:
        selected_cafe.coffee_price = price
        db.session.commit()
        return jsonify(response)
    else:
        response = {
            "error": "there is no cafe with that id"
        }

        return jsonify(response), 404



# HTTP DELETE - Delete Record

@app.route("/delete_cafe/<int:id>", methods=["DELETE"])
def delete_cafe(id):
    if request.args["apiKey"] == "elumeze8":
        selected_cafe = Cafe.query.filter_by(id=id).first()
        if selected_cafe is not None:
            db.session.delete(selected_cafe)
            db.session.commit()
            return jsonify(
                success="successfully deleted"
            ), 200
        else:
            return jsonify(
                error=f"no cafe exist with id '{id}'"
            ), 404
    else:
        return jsonify(
            error="not authorized"
        )


def cafe_to_dict(cafe):
    new_cafe = {
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "seats": cafe.seats,
        "amenities": {
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
        },
        "coffee_price": cafe.coffee_price
    }
    return new_cafe


if __name__ == '__main__':
    app.run(debug=True)
