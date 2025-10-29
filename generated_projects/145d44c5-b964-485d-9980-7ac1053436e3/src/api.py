from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

tasks = {}

class TaskList(Resource):
    def get(self):
        return jsonify(list(tasks.values()))

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        args = parser.parse_args(strict=True)

        task_id = max(tasks.keys(), default=0) + 1
        task = {'id': task_id, 'title': args['title'], 'description': args['description']}
        tasks[task_id] = task
        
        return task, 201

class Task(Resource):
    def get(self, task_id):
        try:
            return tasks[task_id]
        except KeyError:
            abort(404, message=f"Task {task_id} not found")

    def put(self, task_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('description', type=str)
        args = parser.parse_args(strict=True)

        if task_id not in tasks:
            abort(404, message=f"Task {task_id} not found")

        task = tasks[task_id]
        task.update(args)
        return task

    def delete(self, task_id):
        try:
            del tasks[task_id]
            return '', 204
        except KeyError:
            abort(404, message=f"Task {task_id} not found")

api.add_resource(TaskList, '/tasks/')
api.add_resource(Task, '/tasks/<int:task_id>')

if __name__ == '__main__':
    app.run(debug=True)