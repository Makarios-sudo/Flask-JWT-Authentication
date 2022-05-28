import datetime
import hashlib
import pymongo
from flask_cors import cross_origin
from bson import ObjectId
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

app = Flask(__name__)

CONNECTION_STRING = "mongodb+srv://makarios:sloovi@mydb.gftifbj.mongodb.net/mydb?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('mydb')
templates_collection = pymongo.collection.Collection(db, 'templates')
users_collection = pymongo.collection.Collection(db, 'users')

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)


@app.route('/register', methods=["POST"])
def registration():
	try:
		Registered_user = request.get_json()
		Registered_user["password"] = hashlib.sha256(Registered_user["password"].encode("utf-8")).hexdigest()
		doc = users_collection.find_one({"email": Registered_user["email"]})
		if not doc:
			users_collection.insert_one(Registered_user)
			return jsonify({'msg': 'Registration Was Successful!!'}), 201
		else:
			return jsonify({'msg': 'That Username is Taken, Please Try a something else'}), 409
	except Exception as ex:
		return jsonify({'msg': 'Ooop, Registration Failed, Try AGain'}), 500


@app.route('/login', methods=["POST"])
def login():
	try:
		login_details = request.get_json()
		registeredUser = users_collection.find_one({'email': login_details['email']})

		if registeredUser:
			encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
			if encrpted_password == registeredUser['password']:
				access_token = create_access_token(identity=str(registeredUser['_id']))
				return jsonify(access_token=access_token), 200

		return jsonify({'msg': 'The username or password is incorrect.'}), 401
	except Exception as ex:
		return jsonify({'msg': 'Ooop, Login Failed, Try AGain'}), 500



@app.route('/')
def flask_mongodb_atlas():
	return "Hello, Welcome To Sloovi", 200


@app.route('/template', methods=["POST"])
@jwt_required()
@cross_origin()
def new_Template():
	try:
		template_data = request.get_json()
		created_data = {
			"template_name": template_data["template_name"],
			"subject": template_data["subject"],
			"body": template_data["body"],
			"user_id": get_jwt_identity()
		}
		templates_collection.insert_one(created_data)
		return jsonify({'msg': 'Request Successful'}), 201
	except Exception as ex:
		return jsonify({'msg': 'Oooop, Something went wrong, Try Again'}), 500



@app.route('/template', methods=["GET"])
@jwt_required()
@cross_origin()
def all_Templates():
	try:
		templates = list(templates_collection.find({"user_id":get_jwt_identity()}))
		for template in templates:
			template['_id'] = str(template['_id'])
			del template['user_id']
		return jsonify({'msg': 'Request Successful', 'data':templates}), 200
	except Exception as ex:
		return jsonify({'msg': 'Oooop, Something went wrong, Try Again'}), 500



@app.route("/template/<id>/", methods=["GET"])
@jwt_required()
@cross_origin()
def single_template(id):
	try:
		template = templates_collection.find_one({"_id": ObjectId(id)})
		if template:
			return jsonify({"msg": str(id) + " Request Successful"})
		return jsonify({'msg': 'Request Unsuccessful'}), 200
	except Exception as ex:
		return jsonify({'msg': 'Oooop, Something went wrong, Try Again'}), 200



@app.route("/template/<id>", methods=["PUT"])
@jwt_required()
@cross_origin()
def update_Template(id):
	request_data = request.get_json()
	update_data = {
		"template_name": request_data["template_name"],
		"subject": request_data["subject"],
        "body": request_data["body"],
		}
	try:
		template = templates_collection.update_one({'_id': ObjectId(id) }, {"$set": update_data})
		if template.modified_count == 1:
			return jsonify({'msg': 'Request Successful'}), 200
		return jsonify({'msg': 'Request Unsuccessful'}), 200
	except Exception as ex:
		return jsonify({'msg': 'Oooop, Something went wrong, Try Again'}), 200



@app.route("/template/<id>", methods=["DELETE"])
@jwt_required()
@cross_origin()
def deleteTemplate(id):
	try:
		template = templates_collection.delete_one({ '_id': ObjectId(id) })
		if template.deleted_count == 1:
			return jsonify({'msg': 'Request Successful'}), 200
		return jsonify({'msg': 'Request Unsuccessful'}), 200
	except Exception as ex:
		return jsonify({'msg': 'Oooop, Something went wrong, Try Again'}), 500


if __name__ == "__main__":
    app.run()