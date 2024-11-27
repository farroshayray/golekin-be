from . import auth
from flask import Flask

@auth.route('/', methods=['GET'])
def testauth():
    return '<div>hello auth </div>'