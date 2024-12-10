from . import auth
from flask import Flask, request, jsonify, Blueprint
from models.users import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_jwt_extended import create_access_token, unset_jwt_cookies, jwt_required, get_jwt_identity

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    fullname = data.get('fullname', '').strip()
    email = data.get('email', '').strip()
    description = data.get('description', '').strip()
    image_url = data.get('image_url', '').strip()
    password = data.get('password', '').strip()
    pin = data.get('pin', '').strip()
    role = data.get('role', '').strip()
    phone_number = data.get('phone_number', '').strip()
    agen_id_value = data.get('agen_id', '').strip()
    
    agen_id = int(agen_id_value) if agen_id_value else None
    location = data.get('location', '').strip()

    if not username or not fullname or not email or not password or not pin or not role or not phone_number:
        return jsonify({'error': 'Please fill all fields'}), 400

    if role in ['pedagang', 'driver'] and not agen_id:
        return jsonify({'error': 'Agen ID must be provided for "pedagang" or "driver" roles'}), 400
    
    if User.query.filter_by(email=email, role=role).first():
        return jsonify({'error': 'Email already exists on the same role'}), 400
    
    if User.query.filter_by(username=username, role=role).first():
        return jsonify({'error': 'Username already exists on the same role'}), 400
    
    if User.query.filter_by(phone_number=phone_number, role=role).first():
        return jsonify({'error': 'phone number already exists on the same role'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    hashed_pin = generate_password_hash(pin, method='pbkdf2:sha256')

    try:
        user = User(username=username, fullname=fullname, email=email, password_hash=hashed_password, 
                    description=description, image_url=image_url, pin_hash=hashed_pin, role=role, phone_number=phone_number, agen_id=agen_id, location=location)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201
    
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()

    if not email or not password or not role:
        return jsonify({'error': 'Email, password, and role are required'}), 400

    user = User.query.filter_by(email=email, role=role).first()

    if not user:
        return jsonify({'error': 'Invalid email, password, or role'}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email, password, or role'}), 401
    
    access_token = create_access_token(identity=str(user.id))

    return jsonify({'message': 'Login successful', 
                    'email': user.email, 
                    'username': user.username,
                    'fullname': user.fullname,
                    'phone_number': user.phone_number,
                    'agen_id': user.agen_id,
                    'role': user.role, 
                    'id': user.id,
                    'image_url': user.image_url,
                    'access_token': access_token}), 200
