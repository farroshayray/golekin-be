from flask import Blueprint, jsonify, request
from models import db
from flask_jwt_extended import get_jwt_identity
from models.users import User
from models.transactions.transaction import Transaction
from models.transactions.transaction_items import TransactionItems
from models.transactions.delivery import Delivery

# Create a Blueprint for transaction related routes
transactions = Blueprint('transactions', __name__)

@transactions.route('/', methods=['GET'])
def transaction():
    return '<div>Transaction</div>'

@transactions.route("/item/update_quantity/<int:item_id>", methods=["PUT"])
def update_item_quantity(item_id):
    """
    Update the quantity of an item in a transaction.
    :param item_id: ID of the transaction item.
    :return: JSON response indicating success or failure.
    """
    data = request.get_json()
    new_quantity = data.get("quantity")

    if new_quantity is None or not isinstance(new_quantity, int) or new_quantity <= 0:
        return jsonify({"error": "Invalid quantity. Quantity must be a positive integer."}), 400

    try:
        # Fetch the transaction item by ID
        item = TransactionItems.query.get(item_id)

        if not item:
            return jsonify({"error": "Transaction item not found."}), 404

        # Update the subtotal based on the product price and new quantity
        product = item.product  # Assuming the product relationship exists
        if not product:
            return jsonify({"error": "Product associated with the transaction item not found."}), 404

        item.quantity = new_quantity
        item.subtotal = product.price * new_quantity

        # Commit the changes to the database
        db.session.commit()

        return jsonify({
            "message": "Item quantity updated successfully.",
            "item": item.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the item quantity.", "details": str(e)}), 500

@transactions.route('/get_transaction', methods=['GET'])
def get_transaction():
    """
    Get a list of all transactions.
    :return: JSON response with transaction data.
    """
    try:
        transactions = Transaction.query.all()

        if not transactions:
            return jsonify({"error": "No transactions found."}), 404

        return jsonify([transaction.to_dict() for transaction in transactions]), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching transactions.", "details": str(e)}), 500

@transactions.route('/get_transaction_item/<int:item_id>', methods=['GET'])
def get_transaction_item(item_id):
    """
    Get a specific transaction item by its ID.
    :param item_id: ID of the transaction item.
    :return: JSON response with the item details.
    """
    try:
        # Fetch the transaction item by ID
        item = TransactionItems.query.get(item_id)

        if not item:
            return jsonify({"error": "Transaction item not found."}), 404

        return jsonify(item.to_dict()), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the transaction item.", "details": str(e)}), 500

@transactions.route('/get_delivery/<int:delivery_id>', methods=['GET'])
def get_delivery(delivery_id):
    """
    Get the delivery details for a transaction.
    :param delivery_id: ID of the delivery.
    :return: JSON response with the delivery details.
    """
    try:
        # Fetch the delivery by ID
        delivery = Delivery.query.get(delivery_id)

        if not delivery:
            return jsonify({"error": "Delivery not found."}), 404

        return jsonify(delivery.to_dict()), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the delivery.", "details": str(e)}), 500

@transactions.route('/item/delete/<int:item_id>', methods=['DELETE'])
def delete_transaction_item(item_id):
    """
    Delete a transaction item.
    :param item_id: ID of the transaction item to delete.
    :return: JSON response indicating success or failure.
    """
    try:
        # Fetch the transaction item by ID
        item = TransactionItems.query.get(item_id)

        if not item:
            return jsonify({"error": "Transaction item not found."}), 404

        # Delete the transaction item
        db.session.delete(item)
        db.session.commit()

        return jsonify({"message": "Transaction item deleted successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the transaction item.", "details": str(e)}), 500
