from . import user
from models.users import User
from flask import Flask, jsonify, request
from models import db, users
from werkzeug.security import check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity


@user.route('/', methods=['GET'])
def test_user():
    return '<div>User</div>'

# market
# get user with 'agen' role
@user.route('/agents', methods=['GET'])
def get_agents():
    agents = User.query.filter_by(role='agen').all()
    if not agents:
        return jsonify({'agents': []}), 200
    
    agents_data = []
    for agent in agents:
        agents_data.append({
            "id": agent.id,
            "username": agent.username,
            "fullname": agent.fullname,
            "email": agent.email,
            "balance": float(agent.balance),  # Convert Decimal to float for JSON serialization
            "phone_number": agent.phone_number,
            "location": agent.location,
            "image_url": agent.image_url,
            "role": agent.role,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "updated_at": agent.updated_at.isoformat() if agent.updated_at else None,
        })
    
    return jsonify({'agents': agents_data}), 200

@user.route('/topup', methods=['POST'])
@jwt_required()
def topup_balance():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        amount = data.get('amount', 0)
        pin = data.get('pin', '')

        if not amount or amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        if not pin:
            return jsonify({"error": "PIN is required"}), 400

        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not check_password_hash(user.pin_hash, pin):
            return jsonify({"error": "Invalid PIN"}), 403

        user.balance += amount
        db.session.commit()

        return jsonify({
            "message": "Top-up successful",
            "balance": float(user.balance)  # Convert Decimal to float
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error during top-up: {e}")
        return jsonify({"error": "An error occurred during top-up", "details": str(e)}), 500
    
@user.route('/get_balance', methods=['GET'])
@jwt_required()
def get_balance():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "balance": float(user.balance)  # Convert Decimal to float
        }), 200

    except Exception as e:
        print(f"Error while getting balance: {e}")
        return jsonify({"error": "An error occurred while getting balance", "details": str(e)}), 500
    
# udpate balance for transaction (plus or minus)
@user.route('/update_balance', methods=['PUT'])
@jwt_required()
def update_balance():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        amount = data.get('amount', 0)
        plus_minus = data.get('plus_minus', '')

        if not amount:
            return jsonify({"error": "Amount is required"}), 400
        if not plus_minus:
            return jsonify({"error": "plus_minus is required"}), 400

        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if plus_minus == 'plus':
            user.balance += amount
        elif plus_minus == 'minus':
            user.balance -= amount
            if user.balance < amount:
                return jsonify({"error": "Insufficient balance"}), 403
        db.session.commit()

        return jsonify({
            "message": "Balance updated successfully",
            "balance": float(user.balance)  # Convert Decimal to float
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error while updating balance: {e}")
        return jsonify({"error": "An error occurred while updating balance", "details": str(e)}), 500