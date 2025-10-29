# Simple REST API for Task Management

This project is a straightforward REST API designed for task management. It is built using Python, leveraging the FastAPI framework for the API creation, SQLAlchemy for ORM, and PostgreSQL as the database backend. The project also utilizes Uvicorn as the ASGI server for running the application and Pydantic for data validation to ensure robust and reliable API endpoints.

## Features

- **Task Creation**: Add tasks with titles, descriptions, and status.
- **Task Retrieval**: Fetch tasks individually by their ID or all tasks together.
- **Task Updating**: Update the details of an existing task including its status.
- **Task Deletion**: Remove tasks that are no longer needed.

## Installation Instructions

To set up the project locally, follow these steps:

1. **Clone the repository**

```bash
git clone https://github.com/your-repository/simple-rest-api-task-management.git
cd simple-rest-api-task-management
```

2. **Set up a virtual environment**

```bash
python -m venv venv
```

- For Windows:

```bash
venv\Scripts\activate
```

- For macOS/Linux:

```bash
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install fastapi sqlalchemy uvicorn psycopg2 pydantic
```

4. **Database Setup**

- Ensure PostgreSQL is installed and running on your system.
- Create a new database for the project.
- Update the database connection string in the application configuration.

5. **Running the application**

```bash
uvicorn main:app --reload
```

This will start the server on `localhost:8000`.

## Usage Examples

Once the server is running, you can interact with the API using any HTTP client. Below are examples using `curl`.

- **Create a Task**

```bash
curl -X 'POST' \
  'http://localhost:8000/tasks/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "New Task",
  "description": "Description of the new task",
  "status": "pending"
}'
```

- **Get All Tasks**

```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/' \
  -H 'accept: application/json'
```

- **Update a Task**

```bash
curl -X 'PUT' \
  'http://localhost:8000/tasks/{task_id}' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Updated Task",
  "description": "Updated description",
  "status": "completed"
}'
```

- **Delete a Task**

```bash
curl -X 'DELETE' \
  'http://localhost:8000/tasks/{task_id}' \
  -H 'accept: application/json'
```

## API Documentation

The FastAPI framework automatically generates documentation for your API. Once the application is running, you can visit `http://localhost:8000/docs` to view the Swagger UI documentation. This documentation provides an interactive interface for testing and understanding the API endpoints.

## License

This project is licensed under the MIT License - see the LICENSE file for details.