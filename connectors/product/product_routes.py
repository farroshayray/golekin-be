from flask import request, jsonify
from models.products import db, Product
from . import products

@products.route('/add_product', methods=['POST'])
def add_product():
    data = request.get_json()
    product_name = data.get('product_name', '').strip()
    qty = data.get('qty', 0)
    description = data.get('description', '').strip()
    price = data.get('price', 0.0)
    stock = data.get('stock', 0)
    category_id = data.get('category_id', None)
    image_url = data.get('image_url', '').strip()
    is_active = data.get('is_active', 1)

    if not product_name or category_id is None or price <= 0 or stock < 0 or qty < 0:
        return jsonify({'error': 'Invalid or missing required fields'}), 400

    try:
        new_product = Product(
            product_name=product_name,
            qty=qty,
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
            'qty': new_product.qty,
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
