#!/usr/bin/env python3

from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify, abort
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Code challenge</h1>'

@app.route('/vendors', methods=['GET'])
def get_vendors():
    vendors = Vendor.query.all()
    return jsonify([{'id': v.id, 'name': v.name} for v in vendors])

@app.route('/vendors/<int:vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    return jsonify(vendor.to_dict(rules=('-vendor_sweets.vendor',)))

@app.route('/sweets', methods=['GET'])
def get_sweets():
    sweets = Sweet.query.all()
    return jsonify([{'id': s.id, 'name': s.name} for s in sweets])

@app.route('/sweets/<int:sweet_id>', methods=['GET'])
def get_sweet(sweet_id):
    sweet = Sweet.query.get(sweet_id)
    if not sweet:
        return jsonify({'error': 'Sweet not found'}), 404, {'Content-Type': 'application/json'}
    return jsonify(sweet.to_dict())

@app.route('/vendor_sweets', methods=['POST'])
def create_vendor_sweet():
    data = request.get_json()
    vendor = Vendor.query.get(data['vendor_id'])
    sweet = Sweet.query.get(data['sweet_id'])
    if not vendor or not sweet:
        abort(404, 'Vendor or Sweet not found')

    try:
        vendor_sweet = VendorSweet(vendor=vendor, sweet=sweet, price=data['price'])
        db.session.add(vendor_sweet)
        db.session.commit()
        return jsonify(vendor_sweet.to_dict()), 201
    except ValueError as e:
        return jsonify({'errors': [str(e)]}), 400

@app.route('/vendor_sweets/<int:vendor_sweet_id>', methods=['DELETE'])
def delete_vendor_sweet(vendor_sweet_id):
    vendor_sweet = VendorSweet.query.get(vendor_sweet_id)
    if not vendor_sweet:
        return jsonify({"error": "VendorSweet not found"}), 404
    db.session.delete(vendor_sweet)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)
