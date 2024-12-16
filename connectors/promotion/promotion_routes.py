
from . import promotion
from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models.products import Promotion
from models import db

@promotion.route('/', methods=['GET'])
def test_promotions():
    return jsonify({'message': 'Promo route is working!'}), 200

@promotion.route('/handle_promotion', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def handle_promotions():
    current_user_id = get_jwt_identity()

    if request.method == 'GET':
        # Fetch all promotions for the current user
        promotions = Promotion.query.filter_by(user_id=current_user_id).all()
        return jsonify([promotion.to_dict() for promotion in promotions]), 200

    if request.method == 'POST':
        # Create a new promotion
        data = request.get_json()
        try:
            promotion = Promotion(
                product_id=data.get('product_id'),
                user_id=current_user_id,
                transaction_id=data.get('transaction_id'),
                scheme=data.get('scheme'),
                description=data.get('description'),
                scheme_percentage=data.get('scheme_percentage'),
                start_date=datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else None,
                end_date=datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else None,
            )
            db.session.add(promotion)
            db.session.commit()
            return jsonify({'message': 'Promotion created successfully', 'promotion': promotion.to_dict()}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    if request.method == 'PUT':
        # Update an existing promotion
        data = request.get_json()
        promotion_id = data.get('id')
        if not promotion_id:
            return jsonify({'error': 'Promotion ID is required'}), 400

        promotion = Promotion.query.filter_by(id=promotion_id, user_id=current_user_id).first()
        if not promotion:
            return jsonify({'error': 'Promotion not found or not authorized'}), 404

        try:
            promotion.product_id = data.get('product_id', promotion.product_id)
            promotion.transaction_id = data.get('transaction_id', promotion.transaction_id)
            promotion.scheme = data.get('scheme', promotion.scheme)
            promotion.scheme_percentage = data.get('scheme_percentage', promotion.scheme_percentage)
            promotion.description = data.get('description', promotion.description)
            promotion.start_date = datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else promotion.start_date
            promotion.end_date = datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else promotion.end_date

            db.session.commit()
            return jsonify({'message': 'Promotion updated successfully', 'promotion': promotion.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    if request.method == 'DELETE':
        # Delete an existing promotion
        data = request.get_json()
        promotion_id = data.get('id')
        if not promotion_id:
            return jsonify({'error': 'Promotion ID is required'}), 400

        promotion = Promotion.query.filter_by(id=promotion_id, user_id=current_user_id).first()
        if not promotion:
            return jsonify({'error': 'Promotion not found or not authorized'}), 404

        try:
            db.session.delete(promotion)
            db.session.commit()
            return jsonify({'message': 'Promotion deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

