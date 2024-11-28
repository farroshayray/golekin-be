from . import auth
from flask import Flask, request, jsonify
from models.users import db, User

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

    user = User(username=username, fullname=fullname, email=email, password_hash=password, pin_hash=pin, role=role, phone_number=phone_number, agen_id=agen_id, location=location)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201