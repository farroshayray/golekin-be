from . import user
from models.users import User
from flask import Flask, jsonify

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