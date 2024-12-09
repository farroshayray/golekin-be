from . import cart
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models.transactions import Transaction, TransactionItems
from models.products import Product
from models.users import User
from models import db
from datetime import datetime

#test blueprint
@cart.route('/', methods=['GET'])
def test_cart():
    return jsonify({'message': 'Cart route is working!'}), 200

# cart list by user id
@cart.route("/list/<int:user_id>", methods=["GET"])
def get_cart(user_id):
    transactions = Transaction.query.filter_by(from_user_id=user_id, status="cart").all()
    return jsonify({"cart": [transaction.to_dict() for transaction in transactions]}), 200


@cart.route("/add/<int:user_id>", methods=["POST"])
def add_to_cart(user_id):
    try:
        data = request.json
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        if not user_id or not product_id or not quantity:
            return jsonify({"error": "Missing required fields"}), 400

        # Fetch the product
        product = Product.query.get(product_id)
        if not product or product.is_active == 0:
            return jsonify({"error": "Product not found or inactive"}), 404

        if product.stock < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

        # Check if there's already a cart transaction for this market_id (product.user_id)
        transaction = Transaction.query.filter_by(
            from_user_id=user_id,
            to_user_id=product.user_id,
            status="cart"
        ).first()

        if not transaction:
            # Create a new transaction if no cart exists
            transaction = Transaction(
                from_user_id=user_id,
                to_user_id=product.user_id,
                driver_id=None,  # Will be assigned later
                total_amount=0.0,  # Will be updated
                type="transfer",
                status="cart",
                created_at=datetime.utcnow()
            )
            db.session.add(transaction)
            db.session.flush()  # Ensure transaction ID is available

        # Check if the product is already in the cart
        transaction_item = TransactionItems.query.filter_by(
            transaction_id=transaction.id,
            product_id=product_id
        ).first()

        if transaction_item:
            # Update the quantity and subtotal
            transaction_item.quantity += quantity
            transaction_item.subtotal += product.price * quantity
        else:
            # Add new item to the cart
            transaction_item = TransactionItems(
                transaction_id=transaction.id,
                product_id=product_id,
                quantity=quantity,
                subtotal=product.price * quantity,
                created_at=datetime.utcnow()
            )
            db.session.add(transaction_item)

        # Update transaction total amount
        transaction.total_amount += product.price * quantity

        # Deduct stock from the product
        product.stock -= quantity

        db.session.commit()

        return jsonify({
            "message": "Product added to cart successfully",
            "transaction": {
                "id": transaction.id,
                "from_user_id": transaction.from_user_id,
                "to_user_id": transaction.to_user_id,
                "status": transaction.status,
                "total_amount": transaction.total_amount,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "subtotal": item.subtotal
                    } for item in transaction.transaction_items
                ]
            }
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        print("Integrity Error:", e)
        return jsonify({"error": "Database integrity error", "details": str(e)}), 500

    except Exception as e:
        db.session.rollback()
        print("General Error:", e)
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

    
@cart.route("/delete/<int:user_id>/<int:product_id>", methods=["DELETE"])
def delete_from_cart(user_id, product_id):
    try:
        # Find the transaction containing the product for the given user
        transaction_item = TransactionItems.query.join(Transaction).filter(
            TransactionItems.product_id == product_id,
            Transaction.from_user_id == user_id,
            Transaction.status == "cart"
        ).first()

        if not transaction_item:
            return jsonify({"error": "Product not found in the cart"}), 404

        # Update the transaction's total amount
        transaction = Transaction.query.get(transaction_item.transaction_id)
        if transaction:
            transaction.total_amount -= transaction_item.subtotal

        # Restore the product's stock
        product = Product.query.get(product_id)
        if product:
            product.stock += transaction_item.quantity

        # Delete the transaction item
        db.session.delete(transaction_item)

        # If the transaction has no more items, delete it as well
        remaining_items = TransactionItems.query.filter_by(transaction_id=transaction.id).count()
        if remaining_items == 0:
            db.session.delete(transaction)

        db.session.commit()

        return jsonify({"message": "Product removed from cart successfully"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
