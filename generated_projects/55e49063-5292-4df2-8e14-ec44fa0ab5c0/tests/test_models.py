import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Assuming a PostgreSQL setup, adjust as necessary

def db_connect():
    conn = psycopg2.connect(
        dbname="your_test_db_name",
        user="your_db_username",
        password="your_db_password",
        host="localhost"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

def setup_module(module):
    """Setup database tables before running tests."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(open("src/models.py", "r").read())
    cursor.close()
    conn.close()

def teardown_module(module):
    """Clean up database tables after tests."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_results, tests, projects, users CASCADE;")
    cursor.close()
    conn.close()

def test_create_project():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (project_idea, executive_summary) VALUES ('Test Project', 'This is a test project.');")
    cursor.execute("SELECT * FROM projects WHERE project_idea='Test Project';")
    project = cursor.fetchone()
    cursor.close()
    conn.close()
    assert project is not None
    assert project[1] == 'Test Project'

def test_create_test_for_project():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (project_idea, executive_summary) VALUES ('Another Test Project', 'Summary of another test.');")
    cursor.execute("SELECT id FROM projects WHERE project_idea='Another Test Project';")
    project_id = cursor.fetchone()[0]
    cursor.execute("""INSERT INTO tests (project_id, test_name, test_description, test_status) 
                      VALUES (%s, 'Unit Test', 'Description of unit test', 'pending');""", (project_id,))
    cursor.execute("SELECT * FROM tests WHERE project_id=%s;", (project_id,))
    test = cursor.fetchone()
    cursor.close()
    conn.close()
    assert test is not None
    assert test[2] == project_id
    assert test[3] == 'Unit Test'

def test_insert_user_with_unique_username_and_email():
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES ('uniqueuser', 'hash', 'user@example.com');")
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES ('uniqueuser2', 'hash2', 'user2@example.com');")
    except psycopg2.IntegrityError as e:
        pytest.fail(f"Unexpected IntegrityError: {e}")
    finally:
        cursor.close()
        conn.close()

def test_fail_insert_duplicate_username():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password_hash, email) VALUES ('sameuser', 'hash', 'email@example.com');")
    with pytest.raises(psycopg2.IntegrityError):
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES ('sameuser', 'anotherhash', 'anotheremail@example.com');")
    cursor.close()
    conn.close()

def test_fail_insert_duplicate_email():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password_hash, email) VALUES ('user1', 'hash1', 'duplicate@example.com');")
    with pytest.raises(psycopg2.IntegrityError):
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES ('user2', 'hash2', 'duplicate@example.com');")
    cursor.close()
    conn.close()

# Add more tests as needed for error handling, edge cases, etc.