from flask import request, jsonify
from models import db
from models.products import Product, ProductReview, Promotion
from models.users import User
from models.products import Category
from . import products
from flask_jwt_extended import jwt_required, get_jwt_identity

@products.route('/test', methods=['GET'])
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


# @products.route('/all_products', methods=['GET'])
# def get_products():
#     products = Product.query.all()
#     return jsonify({'products': [product.to_dict() for product in products]}), 200

@products.route('/all_products', methods=['GET'])
def get_products():
    try:
        # Fetch all products
        all_products = Product.query.all()
        
        # Prepare the response with promotions
        response_data = []
        for product in all_products:
            # Fetch the promotion for the current product
            promotion = Promotion.query.filter_by(product_id=product.id).first()
            promotion_data = promotion.to_dict() if promotion else None

            # Append product with its promotion details
            product_data = product.to_dict()
            product_data['promotion'] = promotion_data
            response_data.append(product_data)

        return jsonify({'products': response_data}), 200

    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching products.', 'details': str(e)}), 500


@products.route('/category_products/<int:category_id>', methods=['GET'])
def get_category_products(category_id):
    print(f"Fetching products for category ID: {category_id}")
    
    # Fetch the category by ID
    category = Category.query.get(category_id)
    if not category:
        print(f"Category ID {category_id} not found")
        return jsonify({'error': 'Category not found'}), 404

    # Fetch products for the given category
    products = Product.query.filter_by(category_id=category_id).all()
    print(f"Products found: {products}")

    # Prepare the response with promotion data
    response_products = []
    for product in products:
        # Find promotion related to the product
        promotion = Promotion.query.filter_by(product_id=product.id).first()
        product_data = product.to_dict()
        product_data['promotion'] = promotion.to_dict() if promotion else None
        response_products.append(product_data)

    return jsonify({
        'category_name': category.category_name,
        'products': response_products
    }), 200


    
# @products.route('/product/<product_id>', methods=['GET'])
# def get_product(product_id):
#     product = Product.query.get(product_id)
#     category_name = Category.query.get(product.category_id).category_name
#     shop_name = User.query.filter_by(id=product.user_id).first()
#     if product:
#         return jsonify({'catogory_name': category_name , 'shop_name': shop_name.fullname, 'product': product.to_dict()}), 200
#     else:
#         return jsonify({'error': 'Product not found'}), 404
    
# @products.route('/product/<int:product_id>', methods=['GET'])
# def get_product(product_id):
#     try:
#         # Fetch product by ID
#         product = Product.query.get(product_id)
#         if not product:
#             return jsonify({'error': 'Product not found'}), 404

#         # Fetch related category name
#         category = Category.query.get(product.category_id)
#         category_name = category.category_name if category else None

#         # Fetch shop (user) information
#         shop = User.query.filter_by(id=product.user_id).first()
#         shop_name = shop.fullname if shop else None

#         # Fetch reviews for the product
#         reviews = ProductReview.query.filter_by(product_id=product_id).all()
#         review_list = [
#             {
#                 "user_id": review.user_id,
#                 "user_fullname": User.query.get(review.user_id).fullname if User.query.get(review.user_id) else "Unknown",
#                 "review_text": review.review_text,
#                 "star_rating": review.star_rating,
#                 "created_at": review.created_at.isoformat() if review.created_at else None
#             }
#             for review in reviews
#         ]

#         # Calculate average star rating
#         average_rating = (
#             sum([review.star_rating for review in reviews]) / len(reviews)
#             if reviews else 0
#         )

#         return jsonify({
#             'category_name': category_name,
#             'shop_name': shop_name,
#             'product': product.to_dict(),
#             'reviews': {
#                 'details': review_list,
#                 'average_rating': average_rating
#             }
#         }), 200

#     except Exception as e:
#         return jsonify({'error': 'An error occurred while fetching the product.', 'details': str(e)}), 500

@products.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        # Fetch product by ID
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Fetch related category name
        category = Category.query.get(product.category_id)
        category_name = category.category_name if category else None

        # Fetch shop (user) information
        shop = User.query.filter_by(id=product.user_id).first()
        shop_name = shop.fullname if shop else None

        # Fetch reviews for the product
        reviews = ProductReview.query.filter_by(product_id=product_id).all()
        review_list = [
            {
                "user_id": review.user_id,
                "user_fullname": User.query.get(review.user_id).fullname if User.query.get(review.user_id) else "Unknown",
                "review_text": review.review_text,
                "star_rating": review.star_rating,
                "created_at": review.created_at.isoformat() if review.created_at else None
            }
            for review in reviews
        ]

        # Calculate average star rating
        average_rating = (
            sum([review.star_rating for review in reviews]) / len(reviews)
            if reviews else 0
        )

        # Fetch promotion for the product
        promotion = Promotion.query.filter_by(product_id=product_id).first()
        promotion_details = promotion.to_dict() if promotion else None

        return jsonify({
            'category_name': category_name,
            'shop_name': shop_name,
            'product': product.to_dict(),
            'reviews': {
                'details': review_list,
                'average_rating': average_rating
            },
            'promotion': promotion_details
        }), 200

    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the product.', 'details': str(e)}), 500


    
    
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
    try:
        # Fetch products for the given agent (user ID)
        products = Product.query.filter_by(user_id=agen_id).all()
        agen = User.query.filter_by(id=agen_id).first()

        if not agen:
            return jsonify({'error': 'Agent not found'}), 404

        if not products:
            return jsonify({'error': 'Products not found'}), 404

        # Add promotions for each product
        product_list = []
        for product in products:
            promotion = Promotion.query.filter_by(product_id=product.id).first()
            product_data = product.to_dict()
            product_data['promotion'] = promotion.to_dict() if promotion else None
            product_list.append(product_data)

        return jsonify({
            'market_name': agen.fullname,
            'products': product_list
        }), 200

    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching agent products.', 'details': str(e)}), 500


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

@products.route('/input_review', methods=['POST'])
@jwt_required()
def add_product_review():
    """
    Endpoint to add a product review.
    Request Body:
    {
        "product_id": 1,
        "review_text": "Great product!"
        "star_rating" : 5
    }
    """
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        review_text = data.get('review_text')
        star_rating = data.get('star_rating')

        if not product_id:
            return jsonify({"error": "Product ID is required."}), 400

        # Get current user ID from JWT
        current_user_id = get_jwt_identity()

        # Validate product
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found."}), 404

        # Create a new review
        new_review = ProductReview(
            product_id=product_id,
            user_id=current_user_id,
            review_text=review_text,
            star_rating=star_rating
        )
        db.session.add(new_review)
        db.session.commit()

        return jsonify({"message": "Review added successfully."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the review.", "details": str(e)}), 500
    
