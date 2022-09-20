import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
# '''
# @TODO implement endpoint
#     GET /drinks
#         it should be a public endpoint
#         it should contain only the drink.short() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''


@app.route('/drinks',methods=['GET'])
def drinks():
    all_drinks = Drink.query.all()
    if all_drinks is None:
        abort(400)
    
    
    return jsonify({
        "success": True,
        "drinks": [d.short() for d in all_drinks]
    }),200
    


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_details(jwt):
    all_drinks = Drink.query.all()
    if all_drinks is None:
        abort(400)
    drinks = [d.long() for d in all_drinks]
    
    return jsonify({
        "success": True,
        "drinks": drinks
    })
    


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    body = request.get_json()
    if body is None:
        abort(401)
        
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    
    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()
    
    all_drinks = Drink.query.all()
    drinks = [d.long() for d in all_drinks]
    
    return jsonify({
        "success": True,
        "drinks": drinks
    })
    
    


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt,drink_id):
    drink = Drink.query.get(drink_id)
    
    if not drink:
        abort(404)

    try: 
        body = request.get_json()
        
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        
        drink.title = title
        drink.recipe = json.dumps(recipe)
        
        drink.update()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
            }), 200
    
    except Exception as e:
        print(e)
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    
    if drink is None:
        abort(404)
        
    drink.delete()
    
    return jsonify({
        "success": True,
        "delete": drink.id
    }), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404
    
@app.errorhandler(400)
def bad_request(error):  
    response = jsonify({
        "success": False,
        "error_code": "bad_request",
        "description": "The request cannot be fulfilled due to bad syntax",
    })
    return response, 400

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "The request was unable to be followed due to semantic errors."
        }), 422

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
# AuthError.status_code sould be 400 or 401
def authentification_failed(error):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": "Unauthorized"
        }), 401