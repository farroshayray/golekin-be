from flask import Flask, jsonify
from . import transaction
from flask_jwt_extended import get_jwt_identity
from models.users import User
from models.transactions import Transaction

@transaction.route('/', methods=['GET'])
def transaction():
    return '<div>Transaction</div>'

