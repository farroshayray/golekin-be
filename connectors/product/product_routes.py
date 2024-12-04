from flask import request, jsonify
from models import db
from models.products import Product
from models.users import User
from models.products import Category
from . import products
from flask_jwt_extended import jwt_required, get_jwt_identity

@products.route('/test', methods=['GET'])
@jwt_required()
def test_product():
    return jsonify({'message': 'Product route is working!'}), 200

@products.route('/add_category', methods=['POST'])
def add_category():
    data = request.get_json()
    category_name = data.get('category_name', '').strip()
    description = data.get('description', '').strip()
    image_url = data.get('image_url', '').strip()

    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400

    new_category = Category(category_name=category_name, description=description, image_url=image_url)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Category added successfully'}), 201
@products.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify({'categories': [{'id': category.id, 'category_name': category.category_name, 'description': category.description, 'image_url': category.image_url} for category in categories]}), 200

@products.route('/add_product', methods=['POST'])
@jwt_required()
def add_product():
    identity = get_jwt_identity()
    user = User.query.filter_by(id=identity).first() if identity else None
    
    user_id = user.id
    data = request.get_json()
    product_name = data.get('product_name', '').strip()
    description = data.get('description', '').strip()
    price = data.get('price', 0.0)
    stock = data.get('stock', 0)
    category_id = data.get('category_id', None)
    image_url = data.get('image_url', '').strip()
    is_active = data.get('is_active', 1)

    if not product_name or category_id is None or price <= 0 or stock < 0:
        return jsonify({'error': 'Invalid or missing required fields'}), 400

    try:
        new_product = Product(
            user_id = user_id,
            product_name=product_name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            image_url=image_url,
            is_active=is_active
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({'message': 'Product added successfully', 'product': {
            'id': new_product.id,
            'product_name': new_product.product_name,
            'description': new_product.description,
            'price': float(new_product.price),
            'stock': new_product.stock,
            'category_id': new_product.category_id,
            'image_url': new_product.image_url,
            'is_active': new_product.is_active,
            'created_at': new_product.created_at
        }}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
