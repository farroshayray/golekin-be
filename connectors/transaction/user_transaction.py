from flask import Blueprint, jsonify, request
import json
from . import transactions
from models import db
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash
from models.users import User
from models.transactions import Transaction
from models.transactions import TransactionItems
from models.transactions import Delivery
from models.products import Promotion, Product, ProductReview
from geopy.distance import geodesic
from decimal import Decimal

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
    
# @transactions.route("/detail/<int:transaction_id>", methods=["GET"])
# def get_transaction_detail(transaction_id):
#     transaction = Transaction.query.filter_by(id=transaction_id, status="cart").first()
#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404
#     return jsonify({"transaction": transaction.to_dict()}), 200

@transactions.route("/detail/<int:transaction_id>", methods=["GET"])
def get_transaction_detail(transaction_id):
    # Fetch the transaction with the given ID and status 'cart'
    transaction = Transaction.query.filter_by(id=transaction_id, status="cart").first()
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    # Serialize the transaction to include items, product details, and promotions
    transaction_dict = transaction.to_dict()
    transaction_dict["items"] = []

    for item in transaction.transaction_items:
        # Fetch the related product for this item
        product = Product.query.get(item.product_id)
        promotion = Promotion.query.filter_by(product_id=product.id).first() if product else None

        # Append item details including product and promotion
        transaction_dict["items"].append({
            "id": item.id,
            "product_id": product.id if product else None,
            "product_name": product.product_name if product else "Unknown",
            "product_price": product.price if product else 0,
            "product_description": product.description if product else "No description available",
            "product_image_url": product.image_url if product else None,
            "quantity": item.quantity,
            "subtotal": item.subtotal,
            "promotion": {
                "id": promotion.id,
                "scheme": promotion.scheme,
                "scheme_percentage": promotion.scheme_percentage,
                "description": promotion.description,
                "start_date": promotion.start_date,
                "end_date": promotion.end_date,
            } if promotion else None,
        })

    # Return the serialized transaction as JSON
    return jsonify({"transaction": transaction_dict}), 200



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
    
@transactions.route("/status_ordered/agent/<int:agent_id>", methods=["GET"])
def get_transactions_by_consumer_ordered(agent_id):
    """
    Get transactions grouped by consumers for a specific agent (market).
    :param agent_id: The ID of the agent (market).
    :return: JSON response with grouped transactions.
    """
    try:
        # Fetch transactions for the given agent where the status is "cart"
        transactions = Transaction.query.filter_by(to_user_id=agent_id, status="ordered").all()

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
    
@transactions.route("/status_completed/agent/<int:agent_id>", methods=["GET"])
def get_transactions_by_consumer_completed(agent_id):
    """
    Get transactions grouped by consumers for a specific agent (market).
    :param agent_id: The ID of the agent (market).
    :return: JSON response with grouped transactions.
    """
    try:
        # Fetch transactions for the given agent where the status is "cart"
        transactions = Transaction.query.filter(Transaction.to_user_id == agent_id, Transaction.status.in_(["completed", "completed(reviewed)"])).all()

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
    
@transactions.route("/status_processed/agent/<int:agent_id>", methods=["GET"])
def get_transactions_by_consumer_processed(agent_id):
    """
    Get transactions grouped by consumers for a specific agent (market).
    :param agent_id: The ID of the agent (market).
    :return: JSON response with grouped transactions.
    """
    try:
        # Fetch transactions for the given agent where the status is "cart"
        transactions = Transaction.query.filter_by(to_user_id=agent_id, status="processed").all()

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
    
@transactions.route("/status_taken/agent/<int:agent_id>", methods=["GET"])
def get_transactions_by_consumer_taken(agent_id):
    """
    Get transactions grouped by consumers for a specific agent (market).
    :param agent_id: The ID of the agent (market).
    :return: JSON response with grouped transactions.
    """
    try:
        # Fetch transactions for the given agent where the status is "cart"
        transactions = Transaction.query.filter_by(to_user_id=agent_id, status="taken").all()

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

@transactions.route("/status_taken_driver/agent/<int:agent_id>/<int:driver_id>", methods=["GET"])
@jwt_required()
def get_transactions_by_consumer_taken_driver(agent_id, driver_id):
    """
    Get transactions grouped by consumers for a specific agent (market).
    :param agent_id: The ID of the agent (market).
    :return: JSON response with grouped transactions.
    """
    try:
        # Fetch transactions for the given agent where the status is "cart"
        transactions = Transaction.query.filter_by(to_user_id=agent_id, status="taken", driver_id=driver_id).all()

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
    
@transactions.route("/assign_driver", methods=["PUT"])
@jwt_required()
def assign_driver():
    """
    Assign a driver to a transaction and update its status to 'taken'.
    Prevents reassignment if a driver is already assigned.
    """
    try:
        # Parse input data
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        driver_id = data.get('driver_id')
        status = data.get('status', 'taken')

        # Validate input
        if not transaction_id or not driver_id:
            return jsonify({"error": "Both transaction_id and driver_id are required."}), 400

        # Fetch the transaction
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found."}), 404

        # Check if a driver is already assigned
        if transaction.driver_id is not None:
            return jsonify({
                "error": "A driver is already assigned to this transaction.", 
                "existing_driver_id": transaction.driver_id
            }), 400

        # Verify driver exists
        driver = User.query.get(driver_id)
        if not driver or driver.role != 'driver':
            return jsonify({"error": "Invalid driver."}), 404

        # Validate status
        if status != 'taken':
            return jsonify({"error": "Invalid status. Only 'taken' is allowed."}), 400

        # Assign the driver and update status
        transaction.driver_id = driver_id
        transaction.status = status
        db.session.commit()

        return jsonify({
            "message": "Driver assigned and transaction status updated successfully.",
            "transaction_id": transaction_id,
            "driver_id": driver_id,
            "status": status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "An error occurred while assigning the driver and updating status.", 
            "details": str(e)
        }), 500


# put user_location on transaction database
@transactions.route('/delivery_location', methods=['PUT'])
@jwt_required()
def update_delivery_location():
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        location = data.get('location')  # Expected format: {"lat": -7.824557, "lng": 110.373333}

        if not transaction_id or not location:
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch the transaction
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404

        # Fetch the agent (to_user_id is the agent ID)
        agent = User.query.filter_by(id=transaction.to_user_id, role='agen').first()
        if not agent or not agent.location:
            return jsonify({'error': 'Agent location not found'}), 404

        # Calculate the distance
        user_location = (location['lat'], location['lng'])
        try:
            agent_location = json.loads(agent.location)  # Agent location should be stored as JSON in DB
            agent_coords = (agent_location['lat'], agent_location['lng'])
            distance_km = geodesic(user_location, agent_coords).kilometers
        except (KeyError, TypeError, ValueError) as e:
            return jsonify({'error': 'Invalid agent location format', 'details': str(e)}), 400

        # Calculate shipping cost (e.g., 5000 per km)
        if distance_km <= 1:
            cost_per_km = 8000;
        elif distance_km <= 2:
            cost_per_km = 6000;
        elif distance_km <= 3:
            cost_per_km = 5000;
        else:
            cost_per_km = 4000; 
            
        shipping_cost = round(distance_km * cost_per_km, 0)
        if shipping_cost < 5000:
            shipping_cost = 5000

        # Update transaction with user location and shipping cost
        transaction.user_location = json.dumps(location)
        transaction.shipping_cost = shipping_cost

        db.session.commit()

        return jsonify({
            'message': 'Delivery location and shipping cost updated successfully',
            'distance_km': round(distance_km, 2),
            'shipping_cost': shipping_cost
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Error updating delivery location and shipping cost:", e)
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500

@transactions.route('/update_description', methods=['PUT'])
@jwt_required()
def update_transaction_description():
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        description = data.get('description')

        if not transaction_id or not description:
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch the transaction
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404

        # Update the description
        transaction.description = description
        db.session.commit()

        return jsonify({'message': 'Description updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print("Error updating transaction description:", e)
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
# update transaction status
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models.users import User

@transactions.route('/update_status', methods=['PUT'])
@jwt_required()
def update_transaction_status():
    try:
        # Parse input data
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        status = data.get('status')

        # Validate input
        if not transaction_id or not status:
            return jsonify({"error": "Both transaction_id and status are required."}), 400

        # Get current user ID from JWT
        current_user_id = get_jwt_identity()

        # Fetch current user to validate PIN
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"error": "User not found."}), 404

        # Fetch transaction from the database
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found."}), 404

        # Optional: Add additional status change validation if needed
        # For example, prevent certain status changes based on current status
        
        # Update the status
        transaction.status = status
        db.session.commit()

        return jsonify({
            "message": "Transaction status updated successfully.",
            "transaction_id": transaction_id,
            "new_status": status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "An error occurred while updating the transaction status.", 
            "details": str(e)
        }), 500
    
@transactions.route('/update_driver_id', methods=['PUT'])
@jwt_required()
def update_transaction_driver_id():
    try:
        # Parse input data
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        driver_id = data.get('driver_id')

        # Validate input
        if not transaction_id or not driver_id:
            return jsonify({"error": "Both transaction_id and status are required."}), 400

        # Fetch transaction from the database
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found."}), 404

        # Update the status
        transaction.driver_id = driver_id
        db.session.commit()

        return jsonify({
            "message": "Transaction status updated successfully.",
            "transaction_id": transaction_id,
            "new_driver_id": driver_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the transaction status.", "details": str(e)}), 500

# @transactions.route('/update_balance_and_status', methods=['PUT'])
# @jwt_required()
# def update_balance_and_status():
#     try:
#         # Parse input data
#         data = request.get_json()
        
#         # Required fields
#         transaction_id = data.get('transaction_id')
#         status = data.get('status')
#         pin_hash = data.get('pin_hash')
#         amount = data.get('amount', 0)
#         plus_minus = data.get('plus_minus', '')

#         # Validate input
#         if not transaction_id or not status:
#             return jsonify({"error": "Both transaction_id and status are required."}), 400
        
#         if not amount:
#             return jsonify({"error": "Amount is required"}), 400
        
#         if not plus_minus:
#             return jsonify({"error": "plus_minus is required"}), 400

#         # Get current user ID from JWT
#         current_user_id = get_jwt_identity()

#         # Fetch current user to validate PIN
#         current_user = User.query.get(current_user_id)
#         if not current_user:
#             return jsonify({"error": "User not found."}), 404

#         # Validate PIN hash
#         if not pin_hash:
#             return jsonify({"error": "PIN is required."}), 400

#         # Check if provided PIN hash matches the user's stored PIN hash
#         if not current_user.pin_hash or not check_password_hash(current_user.pin_hash, pin_hash):
#             return jsonify({"error": "Invalid PIN."}), 401

#         # Fetch transaction from the database
#         transaction = Transaction.query.get(transaction_id)
#         if not transaction:
#             return jsonify({"error": "Transaction not found."}), 404

#         # Update balance
#         if plus_minus == 'plus':
#             current_user.balance += amount
#         elif plus_minus == 'minus':
#             if current_user.balance < amount:
#                 return jsonify({"error": "Insufficient balance"}), 403
#             current_user.balance -= amount
#         else:
#             return jsonify({"error": "Invalid plus_minus value. Must be 'plus' or 'minus'"}), 400

#         # Update transaction status
#         transaction.status = status

#         # Commit changes
#         db.session.commit()

#         return jsonify({
#             "message": "Balance and transaction status updated successfully",
#             "transaction_id": transaction_id,
#             "new_status": status,
#             "balance": float(current_user.balance)
#         }), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({
#             "error": "An error occurred while processing the request.", 
#             "details": str(e)
#         }), 500

@transactions.route('/update_balance_and_status', methods=['PUT'])
@jwt_required()
def update_balance_and_status():
    try:
        # Parse input data
        data = request.get_json()

        # Required fields
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        pin_hash = data.get('pin_hash')
        amount = Decimal(data.get('amount', 0))  # Convert to Decimal
        plus_minus = data.get('plus_minus', '')

        # Validate input
        if not transaction_id or not status:
            return jsonify({"error": "Both transaction_id and status are required."}), 400
        
        if not amount:
            return jsonify({"error": "Amount is required"}), 400
        
        if not plus_minus:
            return jsonify({"error": "plus_minus is required"}), 400

        # Get current user ID from JWT
        current_user_id = get_jwt_identity()

        # Fetch current user to validate PIN
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"error": "User not found."}), 404

        # Validate PIN hash
        if not pin_hash:
            return jsonify({"error": "PIN is required."}), 400

        if not current_user.pin_hash or not check_password_hash(current_user.pin_hash, pin_hash):
            return jsonify({"error": "Invalid PIN."}), 401

        # Fetch transaction from the database
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found."}), 404

        # Initialize cashback total and recalculate total_amount
        cashback_total = Decimal(0)  # Ensure cashback_total is a Decimal
        updated_total_amount = Decimal(0)  # To calculate the new total amount for the transaction

        # Iterate through transaction items
        for item in transaction.transaction_items:
            # Fetch the associated product and promotion
            product = Product.query.get(item.product_id)
            promotion = Promotion.query.filter_by(product_id=item.product_id).first()

            if promotion:
                if promotion.scheme == 'discount':
                    # Apply discount to the product subtotal
                    discount = (Decimal(promotion.scheme_percentage) / 100) * Decimal(item.subtotal)
                    item.subtotal = Decimal(item.subtotal) - discount
                elif promotion.scheme == 'cashback':
                    # Calculate cashback and add it to the user's balance
                    cashback = (Decimal(promotion.scheme_percentage) / 100) * Decimal(item.subtotal)
                    cashback_total += cashback

            # Add item's updated subtotal to the new total_amount
            updated_total_amount += Decimal(item.subtotal)

        # Update transaction's total_amount with the recalculated value
        transaction.total_amount = updated_total_amount

        # Update user's balance with cashback
        if cashback_total > 0:
            current_user.balance = Decimal(current_user.balance) + cashback_total

        # Update balance based on plus_minus
        if plus_minus == 'plus':
            current_user.balance = Decimal(current_user.balance) + amount
        elif plus_minus == 'minus':
            if Decimal(current_user.balance) < updated_total_amount:
                return jsonify({"error": "Insufficient balance"}), 403
            current_user.balance = Decimal(current_user.balance) - updated_total_amount - Decimal(transaction.shipping_cost)
        else:
            return jsonify({"error": "Invalid plus_minus value. Must be 'plus' or 'minus'"}), 400

        # Update transaction status
        transaction.status = status

        # Commit changes
        db.session.commit()

        return jsonify({
            "message": "Balance and transaction status updated successfully",
            "transaction_id": transaction_id,
            "new_status": status,
            "balance": float(current_user.balance),  # Convert Decimal to float for JSON serialization
            "updated_total_amount": float(updated_total_amount)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "An error occurred while processing the request.",
            "details": str(e)
        }), 500



@transactions.route('/update_driver_location', methods=['PUT'])
@jwt_required()
def update_driver_location():
    """
    Update the driver's location for all transactions with the same driver_id and status 'taken'.
    """
    try:
        # Parse input data
        data = request.get_json()
        driver_id = data.get('driver_id')
        driver_location = data.get('driver_location')

        # Validate input
        if not driver_id or not driver_location:
            return jsonify({"error": "Both driver_id and driver_location are required."}), 400

        # Ensure driver_location is valid JSON
        try:
            location_data = json.loads(driver_location)
            if not all(key in location_data for key in ['lat', 'lng']):
                raise ValueError("Invalid driver_location format. Required keys: lat, lng.")
        except (ValueError, TypeError) as e:
            return jsonify({"error": "Invalid driver_location format.", "details": str(e)}), 400

        # Fetch transactions with the same driver_id and status 'taken'
        transactions = Transaction.query.filter_by(driver_id=driver_id, status='taken').all()

        if not transactions:
            return jsonify({"error": "No transactions with status 'taken' found for the given driver_id."}), 200

        # Update driver location for all applicable transactions
        for transaction in transactions:
            transaction.driver_location = driver_location

        db.session.commit()

        return jsonify({
            "message": "Driver location updated successfully for all applicable transactions.",
            "updated_transactions": [transaction.id for transaction in transactions],
            "driver_location": driver_location
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating driver location.", "details": str(e)}), 500

@transactions.route("/transaction_list/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_transactions_by_user(user_id):
    """
    Get all transactions for a specific user based on the from_user_id column.
    :param user_id: The ID of the user.
    :return: JSON response with the user's transactions.
    """
    try:
        # Fetch transactions where the from_user_id matches the user_id
        transactions = Transaction.query.filter_by(from_user_id=user_id).all()

        if not transactions:
            return jsonify({"message": "No transactions found for this user."}), 404

        # Convert transactions to dictionary format for JSON serialization
        transactions_list = [transaction.to_dict() for transaction in transactions]

        return jsonify({"user_id": user_id, "transactions": transactions_list}), 200

    except Exception as e:
        print("Error fetching transactions for user:", e)
        return jsonify({"error": "An error occurred while fetching transactions.", "details": str(e)}), 500
    
#get driver_location from transactions table by transaction id
@transactions.route('/driver_location/<int:transaction_id>', methods=['GET'])
def get_driver_location(transaction_id):
    try:
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found."}), 404

        return jsonify({"driver_location": transaction.driver_location}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching driver location.", "details": str(e)}), 500

@transactions.route('/update_status_completed', methods=['PUT'])
@jwt_required()
def update_transaction_status_completed():
    try:
        # Parse input data
        data = request.get_json()
        transaction_id = data.get('transaction_id')

        # Validate input
        if not transaction_id:
            return jsonify({"error": "Transaction ID is required."}), 400

        # Get current user ID from JWT
        current_user_id = get_jwt_identity()

        # Fetch current user
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"error": "User not found."}), 404

        # Fetch transaction from the database
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found."}), 404

        # Update balance for to_user_id
        to_user = User.query.get(transaction.to_user_id)
        if not to_user:
            return jsonify({"error": "Recipient user not found."}), 404

        to_user.balance += Decimal(transaction.total_amount)

        # Update balance for driver_id
        if transaction.driver_id:
            driver = User.query.get(transaction.driver_id)
            if not driver:
                return jsonify({"error": "Driver user not found."}), 404

            driver.balance += Decimal(transaction.shipping_cost)

        # Update transaction status to 'completed'
        transaction.status = 'completed'

        # Commit changes to the database
        db.session.commit()

        return jsonify({
            "message": "Transaction status updated and balances adjusted successfully.",
            "transaction_id": transaction_id,
            "to_user_balance": to_user.balance,
            "driver_balance": driver.balance if transaction.driver_id else None
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "An error occurred while updating the transaction status.",
            "details": str(e)
        }), 500
