from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Association Table for many-to-many relationship between User and Task
user_task_table = Table('user_task', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('task_id', ForeignKey('tasks.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    tasks = relationship("Task", secondary=user_task_table, back_populates="assigned_users")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    assigned_users = relationship("User", secondary=user_task_table, back_populates="tasks")