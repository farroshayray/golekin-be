from flask import Flask, jsonify, request
from . import transactions
from models import db
from flask_jwt_extended import get_jwt_identity
from models.users import User
from models.transactions import Transaction, TransactionItems

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
        product = item.product
        if not product:
            return jsonify({"error": "Product associated with the transaction item not found."}), 404

        item.quantity = new_quantity
        item.subtotal = product.price * new_quantity

        # Commit the changes
        db.session.commit()

        return jsonify({
            "message": "Item quantity updated successfully.",
            "item": item.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the item quantity.", "details": str(e)}), 500

