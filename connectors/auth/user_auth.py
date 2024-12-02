from . import auth
from flask import Flask, request, jsonify, Blueprint
from models.users import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    fullname = data.get('fullname', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    pin = data.get('pin', '').strip()
    role = data.get('role', '').strip()
    phone_number = data.get('phone_number', '').strip()
    agen_id_value = data.get('agen_id', '').strip()  # Get and strip the value
    agen_id = int(agen_id_value) if agen_id_value else None
    location = data.get('location', '').strip()

    if not username or not fullname or not email or not password or not pin or not role or not phone_number:
        return jsonify({'error': 'Please fill all fields'}), 400
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    hashed_pin = generate_password_hash(pin, method='pbkdf2:sha256')
    user = User(username=username, fullname=fullname, email=email, password_hash=hashed_password, pin_hash=hashed_pin, role=role, phone_number=phone_number, agen_id=agen_id, location=location)
    
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

    return jsonify({'message': 'Login successful', 'user': user.email}), 200
