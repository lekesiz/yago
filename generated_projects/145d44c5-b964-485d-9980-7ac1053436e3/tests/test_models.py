import pytest
from datetime import datetime, timedelta
from src.models import TaskCreate, TaskUpdate, Task, TaskList

# Fixture for TaskCreate data
@pytest.fixture(scope="module")
def task_create_data():
    return {
        "title": "Complete the project",
        "description": "Need to finish the backend and frontend by the end of the week",
        "due_date": datetime(2023, 12, 31, 23, 59, 59)
    }

# Fixture for TaskUpdate data
@pytest.fixture(scope="module")
def task_update_data():
    return {
        "title": "Complete the project updated",
        "description": "Additional details added to the task",
        "due_date": datetime(2023, 12, 30, 23, 59, 59),
        "completed": True
    }

# Happy path tests
def test_task_create_model(task_create_data):
    task_create = TaskCreate(**task_create_data)
    assert task_create.title == task_create_data["title"]
    assert task_create.description == task_create_data["description"]
    assert task_create.due_date == task_create_data["due_date"]

def test_task_update_model(task_update_data):
    task_update = TaskUpdate(**task_update_data)
    assert task_update.title == task_update_data["title"]
    assert task_update.description == task_update_data["description"]
    assert task_update.due_date == task_update_data["due_date"]
    assert task_update.completed == task_update_data["completed"]

# Edge case tests
def test_task_create_title_length():
    with pytest.raises(ValueError):
        TaskCreate(title='x' * 101)

def test_task_create_description_length():
    with pytest.raises(ValueError):
        TaskCreate(title="Valid Title", description='x' * 501)

def test_task_update_empty_data():
    task_update = TaskUpdate()
    assert task_update.title is None
    assert task_update.description is None
    assert task_update.due_date is None
    assert task_update.completed is None

# Error handling tests
def test_task_create_invalid_due_date():
    with pytest.raises(ValueError):
        TaskCreate(title="Valid Title", due_date="invalid-date-format")

def test_task_list_model():
    task = Task(
        id=1,
        title="Complete the project",
        description="Need to finish the backend and frontend by the end of the week",
        due_date=datetime.now() + timedelta(days=1),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        completed=False
    )
    task_list = TaskList(tasks=[task])
    assert len(task_list.tasks) == 1
    assert task_list.tasks[0].title == task.title

# Test Task Model Configuration
def test_task_model_config():
    task_data = {
        "id": 1,
        "title": "Test Task",
        "description": "Testing the Task model",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "completed": False
    }
    task = Task(**task_data)
    assert task.Config.orm_mode is True