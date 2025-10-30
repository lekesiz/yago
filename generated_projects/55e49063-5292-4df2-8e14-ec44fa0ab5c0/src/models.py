CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    project_idea VARCHAR(255) NOT NULL,
    executive_summary TEXT NOT NULL
);

CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    test_description TEXT,
    test_status ENUM('pending', 'running', 'passed', 'failed') NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE test_results (
    id SERIAL PRIMARY KEY,
    test_id INTEGER NOT NULL,
    result_data JSON NOT NULL,
    passed BOOLEAN NOT NULL,
    run_time FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES tests(id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash CHAR(64) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE project_users (
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role ENUM('admin', 'developer', 'tester') NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    PRIMARY KEY (project_id, user_id)
);