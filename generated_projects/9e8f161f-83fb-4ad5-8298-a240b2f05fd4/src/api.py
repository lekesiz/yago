from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from http import HTTPStatus

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    email = fields.Email(required=True)

class TaskSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str()
    due_date = fields.Date()
    completed = fields.Bool(default=False)

user_schema = UserSchema()
task_schema = TaskSchema()

users = []
tasks = []

@app.route('/auth/token', methods=['POST'])
def generate_token():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"message": "Username and password are required"}), HTTPStatus.BAD_REQUEST
        
        user = next((user for user in users if user['username'] == username and user['password'] == password), None)
        if not user:
            return jsonify({"message": "Invalid username or password"}), HTTPStatus.UNAUTHORIZED
        
        access_token = create_access_token(identity=user['id'])
        return jsonify({"access_token": access_token}), HTTPStatus.OK
    except:
        return jsonify({"message": "An error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        errors = user_schema.validate(data)
        if errors:
            return jsonify(errors), HTTPStatus.BAD_REQUEST
        
        user = user_schema.load(data)
        user['id'] = len(users) + 1
        users.append(user)
        return jsonify(user_schema.dump(user)), HTTPStatus.CREATED
    except ValidationError as err:
        return jsonify(err.messages), HTTPStatus.BAD_REQUEST
    except:
        return jsonify({"message": "An error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    try:
        user = next((user for user in users if user['id'] == user_id), None)
        if not user:
            return jsonify({"message": "User not found"}), HTTPStatus.NOT_FOUND
        
        return jsonify(user_schema.dump(user)), HTTPStatus.OK
    except:
        return jsonify({"message": "An error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/tasks', methods=['POST'])
@jwt_required
def create_task():
    try:
        data = request.get_json()
        errors = task_schema.validate(data)
        if errors:
            return jsonify(errors), HTTPStatus.BAD_REQUEST
        
        task = task_schema.load(data)
        task['id'] = len(tasks) + 1
        task['user_id'] = get_jwt_identity()
        tasks.append(task)
        return jsonify(task_schema.dump(task)), HTTPStatus.CREATED
    except ValidationError as err:
        return jsonify(err.messages), HTTPStatus.BAD_REQUEST
    except:
        return jsonify({"message": "An error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/tasks', methods=['GET'])
@jwt_required
def get_tasks():
    try:
        user_id = get_jwt_identity()
        user_tasks = [task for task in tasks if task['user_id'] == user_id]
        return jsonify(task_schema.dump(user_tasks, many=True)), HTTPStatus.OK
    except:
        return jsonify({"message": "An error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required
def get_task(task_id):
    try:
        user_id = get_jwt_identity()
        task = next((task for task in tasks if task['id'] == task_id and task['user_id'] == user_id), None)
        if not task:
            return jsonify({"message": "Task not found"}), HTTPStatus.NOT_FOUND
        
        return jsonify(task_schema.dump(task)), HTTPStatus.OK
    except:
        return jsonify({"message": "An error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required
def update_task(task_id):
    try:
        user_id = get_jwt_identity()
        task = next((task for task in tasks if task['id'] == task_id and task['user_id'] == user_id), None)
        if not task:
            return jsonify({"message": "Task not found"}), HTTPStatus.NOT_FOUND
        
        data = request.get_json()
        errors = task_schema.validate(data, partial=True)
        if errors:
            return jsonify(errors), HTTPStatus.BAD_REQUEST
        
        updated_task = task_schema.load(data, partial=True)
        task.update(updated_task)
        return jsonify(task_schema.dump(task)), HTTPStatus.OK
    except ValidationError as err:
        return jsonify(err.messages), HTTPStatus.BAD_REQUEST
    except:
        return jsonify({"message": "An error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required
def delete_task(task_id):
    try:
        user_id = get_jwt_identity()
        task = next((task for task in tasks if task['id'] == task_id and task['user_id'] == user_id), None)
        if not task:
            return jsonify({"message": "Task not found"}), HTTPStatus.NOT_FOUND
        
        tasks.remove(task)
        return '', HTTPStatus.NO_CONTENT
    except:
        return jsonify({"message": "An error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == '__main__':
    app.run()