from flask import request, jsonify
from models import db
from models.agens import Agen
from . import agen

@agen.route('/add_agen', methods=['POST'])
def create_agen():
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')

    if not name or not location:
        return jsonify({"error": "Name and location are required"}), 400

    new_agen = Agen(name=name, location=location)
    db.session.add(new_agen)
    db.session.commit()

    return jsonify({
        "id": new_agen.id,
        "name": new_agen.name,
        "location": new_agen.location,
        "is_open": new_agen.is_open,
        "created_at": new_agen.created_at
    }), 201

@agen.route('/all_agens', methods=['GET'])
def get_agens():
    agens= Agen.query.all()
    return jsonify([
        {
            "id": agen.id,
            "name": agen.name,
            "location": agen.location,
            "is_open": agen.is_open,
            "created_at": agen.created_at,
            "updated_at": agen.updated_at
        }
        for agen in agens
    ])

@agen.route('/edit_agen/<int:agen_id>', methods=['PUT'])
def update_agen(agen_id):
    data = request.get_json()
    agen = Agen.query.get(agen_id)

    if not agen:
        return jsonify({"error": "Agen not found"}), 404

    name = data.get('name')
    location = data.get('location')
    is_open = data.get('is_open')

    if name:
        agen.name = name
    if location:
        agen.location = location
    if is_open is not None:
        agen.is_open = is_open

    db.session.commit()

    return jsonify({
        "id": agen.id,
        "name": agen.name,
        "location": agen.location,
        "is_open": agen.is_open,
        "created_at": agen.created_at,
        "updated_at": agen.updated_at
    })

@agen.route('/delete_agen/<int:agen_id>', methods=['DELETE'])
def delete_agen(agen_id):
    agen = Agen.query.get(agen_id)

    if not agen:
        return jsonify({"error": "Agen not found"}), 404

    db.session.delete(agen)
    db.session.commit()

    return jsonify({"message": "Agen deleted successfully"}), 200
