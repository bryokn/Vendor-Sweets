from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Sweet(db.Model, SerializerMixin):
    __tablename__ = 'sweets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    vendor_sweets = db.relationship('VendorSweet', backref='sweet', cascade='all, delete-orphan')
    vendors = association_proxy('vendor_sweets', 'vendor')

    serialize_rules = ('-vendor_sweets', '-vendors')

    def __repr__(self):
        return f'<Sweet {self.id}>'

class Vendor(db.Model, SerializerMixin):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    vendor_sweets = db.relationship('VendorSweet', backref='vendor', cascade='all, delete-orphan')
    sweets = association_proxy('vendor_sweets', 'sweet')

    serialize_rules = ('-vendor_sweets.vendor',)

    def __repr__(self):
        return f'<Vendor {self.id}>'


class VendorSweet(db.Model, SerializerMixin):
    __tablename__ = 'vendor_sweets'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    sweet_id = db.Column(db.Integer, db.ForeignKey('sweets.id', ondelete='CASCADE'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id', ondelete='CASCADE'), nullable=False)

    serialize_rules = ('-sweet.vendor_sweets', '-vendor.vendor_sweets')

    @validates('price')
    def validate_price(self, key, value):
        if value is None:
            raise ValueError('Price cannot be None')
        if value < 0:
            raise ValueError('Price cannot be negative')
        return value

    def __repr__(self):
        return f'<VendorSweet {self.id}>'