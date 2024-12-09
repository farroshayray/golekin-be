from flask import Blueprint, jsonify, request
from . import transactions
from models import db
from flask_jwt_extended import get_jwt_identity
from models.users import User
from models.transactions import Transaction
from models.transactions import TransactionItems
from models.transactions import Delivery

# Create a Blueprint for transaction related routes

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

@transactions.route("/status_cart/agent/<int:agent_id>", methods=["GET"])
def get_transactions_by_consumer(agent_id):
    """
    Get transactions grouped by consumers for a specific agent (market).
    :param agent_id: The ID of the agent (market).
    :return: JSON response with grouped transactions.
    """
    try:
        # Fetch transactions for the given agent where the status is "cart"
        transactions = Transaction.query.filter_by(to_user_id=agent_id, status="cart").all()

        if not transactions:
            return jsonify({"message": "No transactions found for this agent."}), 404

        # Group transactions by consumers (from_user_id)
        grouped_transactions = {}
        for transaction in transactions:
            consumer_id = transaction.from_user_id
            if consumer_id not in grouped_transactions:
                # Add consumer to the group with their details
                consumer = User.query.get(consumer_id)
                grouped_transactions[consumer_id] = {
                    "consumer_id": consumer_id,
                    "consumer_name": consumer.fullname if consumer else "Unknown",
                    "transactions": [],
                }
            
            # Add the transaction to the consumer's group
            grouped_transactions[consumer_id]["transactions"].append(transaction.to_dict())

        # Convert the grouped transactions to a list for JSON serialization
        grouped_transactions_list = list(grouped_transactions.values())

        return jsonify({"grouped_transactions": grouped_transactions_list}), 200

    except Exception as e:
        print("Error fetching transactions by consumer:", e)
        return jsonify({"error": "An error occurred while fetching transactions.", "details": str(e)}), 500
