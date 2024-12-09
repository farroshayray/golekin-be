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

#products

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
    
@products.route('/update_product/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    identity = get_jwt_identity()
    user = User.query.filter_by(id=identity).first() if identity else None

    # Get the product by its ID
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.user_id != user.id:
        return jsonify({'error': 'You are not authorized to edit this product'}), 403

    data = request.get_json()

    # Get and validate the updated product fields
    product_name = data.get('product_name', product.product_name).strip()
    description = data.get('description', product.description).strip()
    price = data.get('price', product.price)
    stock = data.get('stock', product.stock)
    category_id = data.get('category_id', product.category_id)
    image_url = data.get('image_url', product.image_url).strip()
    is_active = data.get('is_active', product.is_active)

    if not product_name or category_id is None or price <= 0 or stock < 0:
        return jsonify({'error': 'Invalid or missing required fields'}), 400

    try:
        # Update the product details
        product.product_name = product_name
        product.description = description
        product.price = price
        product.stock = stock
        product.category_id = category_id
        product.image_url = image_url
        product.is_active = is_active

        db.session.commit()

        return jsonify({'message': 'Product updated successfully', 'product': {
            'id': product.id,
            'product_name': product.product_name,
            'description': product.description,
            'price': float(product.price),
            'stock': product.stock,
            'category_id': product.category_id,
            'image_url': product.image_url,
            'is_active': product.is_active,
            'created_at': product.created_at,
            'updated_at': product.updated_at
        }}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@products.route('/all_products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify({'products': [product.to_dict() for product in products]}), 200

@products.route('/category_products/<int:category_id>', methods=['GET'])
def get_category_products(category_id):
    print(f"Fetching products for category ID: {category_id}")
    category = Category.query.get(category_id)
    if not category:
        print(f"Category ID {category_id} not found")
        return jsonify({'error': 'Category not found'}), 404

    products = Product.query.filter_by(category_id=category_id).all()
    print(f"Products found: {products}")
    return jsonify({
        'category_name': category.category_name,
        'products': [product.to_dict() for product in products]
    }), 200

    
@products.route('/product/<product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    category_name = Category.query.get(product.category_id).category_name
    shop_name = User.query.filter_by(id=product.user_id).first()
    if product:
        return jsonify({'catogory_name': category_name , 'shop_name': shop_name.fullname, 'product': product.to_dict()}), 200
    else:
        return jsonify({'error': 'Product not found'}), 404
    
    
# categories
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

@products.route('/category/<category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    return jsonify({'category': {'id': category.id, 'category_name': category.category_name, 'description': category.description, 'image_url': category.image_url}}), 200

# semua product yang dibuat oleh sebuah agen
@products.route('/agen_products/<int:agen_id>', methods=['GET'])
def get_agen_products(agen_id):
    products = Product.query.filter_by(user_id=agen_id).all()
    agen_name = User.query.filter_by(id=agen_id).first().fullname
    if not products:
        return jsonify({'error': 'Products not found'}), 404
    return jsonify({'market_name': agen_name, 'products': [product.to_dict() for product in products]}), 200

@products.route('/delete_product/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    identity = get_jwt_identity()
    user = User.query.filter_by(id=identity).first() if identity else None

    # Check if the product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Check if the user is authorized to delete the product
    if product.user_id != user.id:
        return jsonify({'error': 'You are not authorized to delete this product'}), 403

    try:
        # Delete the product
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
