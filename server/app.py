#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

class Plants(Resource):
    def get(self):
        plants = Plant.query.all()
        return [plant.to_dict() for plant in plants], 200

    def post(self):
        data = request.get_json()

        if not data or 'name' not in data or 'image' not in data or 'price' not in data:
            return {"error": "Missing required fields (name, image, price)"}, 400

        try:
            new_plant = Plant(
                name=data['name'],
                image=data['image'],
                price=float(data['price']),
                is_in_stock=data.get('is_in_stock', True)
            )
            db.session.add(new_plant)
            db.session.commit()

            return new_plant.to_dict(), 201

        except ValueError:
            db.session.rollback()
            return {"error": "Invalid price value"}, 400

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.get(id)
        if not plant:
            return {"error": "Plant not found"}, 404
        return plant.to_dict(), 200

    def patch(self, id):
        plant = Plant.query.get(id)
        if not plant:
            return {"error": "Plant not found"}, 404

        data = request.get_json()
        if not data or 'is_in_stock' not in data:
            return {"error": "No valid data provided"}, 400

        try:
            plant.is_in_stock = data['is_in_stock']
            db.session.commit()
            return plant.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, id):
        plant = Plant.query.get(id)
        if not plant:
            return {"error": "Plant not found"}, 404

        try:
            db.session.delete(plant)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

api.add_resource(Plants, '/plants')
api.add_resource(PlantByID, '/plants/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)