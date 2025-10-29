import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.models import Base, User, Task, user_task_table
from sqlalchemy.exc import IntegrityError

# Setup for database connection, using an in-memory SQLite database for tests
@pytest.fixture(scope="module")
def database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=engine))
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def session(database):
    database.begin_nested()  # Start a savepoint
    yield database
    database.rollback()  # Rollback operations between tests

def test_create_user(session):
    new_user = User(username="testuser", email="test@example.com", hashed_password="hashedpassword")
    session.add(new_user)
    session.commit()
    assert new_user.id is not None

def test_create_task(session):
    new_task = Task(title="Test Task")
    session.add(new_task)
    session.commit()
    assert new_task.id is not None

def test_user_unique_username_constraint(session):
    session.add(User(username="uniqueuser", email="unique@example.com", hashed_password="hashedpassword"))
    session.commit()
    with pytest.raises(IntegrityError):
        session.add(User(username="uniqueuser", email="different@example.com", hashed_password="anotherpassword"))
        session.commit()

def test_user_unique_email_constraint(session):
    session.add(User(username="user1", email="uniqueemail@example.com", hashed_password="hashedpassword"))
    session.commit()
    with pytest.raises(IntegrityError):
        session.add(User(username="user2", email="uniqueemail@example.com", hashed_password="anotherpassword"))
        session.commit()

def test_assign_task_to_user(session):
    user = User(username="taskuser", email="taskuser@example.com", hashed_password="hashedpassword")
    task = Task(title="Assigned Task")
    user.tasks.append(task)
    session.add(user)
    session.commit()
    assert task in user.tasks

def test_remove_task_from_user(session):
    user = User(username="removetaskuser", email="removetaskuser@example.com", hashed_password="hashedpassword")
    task = Task(title="Task to Remove")
    user.tasks.append(task)
    session.add(user)
    session.commit()
    user.tasks.remove(task)
    session.commit()
    assert task not in user.tasks

def test_task_assigned_to_multiple_users(session):
    user1 = User(username="multiuser1", email="multiuser1@example.com", hashed_password="hashedpassword")
    user2 = User(username="multiuser2", email="multiuser2@example.com", hashed_password="hashedpassword")
    task = Task(title="Shared Task")
    user1.tasks.append(task)
    user2.tasks.append(task)
    session.add_all([user1, user2])
    session.commit()
    assert task in user1.tasks
    assert task in user2.tasks

def test_delete_user_cascades_to_association_table_not_task(session):
    user = User(username="deleteuser", email="deleteuser@example.com", hashed_password="hashedpassword")
    task = Task(title="Persisting Task")
    user.tasks.append(task)
    session.add(user)
    session.commit()
    session.delete(user)
    session.commit()
    assert session.query(Task).filter(Task.id == task.id).count() == 1
    assert session.query(user_task_table).filter(user_task_table.c.user_id == user.id).count() == 0

# Note: Depending on the cascade configuration in the relationship, the last test might need adjustment.
# This test assumes tasks are not deleted when a user is deleted, only the association is removed.