import pytest
from app import app
from flask import json
from bson import ObjectId
import os
from pymongo import MongoClient

DB_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "mymongodb")

client = MongoClient(DB_URI)
db = client[DB_NAME]
todos = db.todo

@pytest.fixture
def client():
    # Create a test client for the Flask app
    with app.test_client() as client:
        yield client

def test_list_tasks(client):
    """Test for listing all tasks"""
    response = client.get("/list")
    assert response.status_code == 200
    assert b'TODO APP' in response.data

def test_add_task(client):
    """Test adding a task"""
    response = client.post('/action', data={
        'name': 'Test Task',
        'desc': 'Description for test task',
        'date': '2024-12-25',
        'pr': 'high'
    })
    assert response.status_code == 302  # Redirection
    assert '/list' in response.location

def test_remove_task(client):
    """Test task deletion"""
    response = client.get('/remove?_id=1234567890abcdef12345678')  # Example _id
    assert response.status_code == 302
    assert '/' in response.location

@pytest.fixture
def setup_database():
    """Setup the database with a mock task."""
    task_id = ObjectId("1234567890abcdef12345678")
    todos.insert_one({
        "_id": task_id,
        "name": "Test Task",
        "desc": "Test Description",
        "date": "2024-01-01",
        "pr": "Low",
        "done": "no"
    })
    yield  # Pass control to the test
    todos.delete_one({"_id": task_id})  # Cleanup after the test

    @pytest.fixture
    def client():
        """Provide a Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client


def test_toggle_task_status(client, setup_database):
    """Test toggling task completion."""
    response = client.get('/done?_id=1234567890abcdef12345678')  # Example _id
    assert response.status_code == 302


def test_search_task(client):
    """Test searching tasks"""
    response = client.get('/search?key=1234567890abcdef12345678&refer=_id')  # Example search criteria
    assert response.status_code == 200
    assert b'No tasks found' not in response.data

def test_delete_all_tasks(client):
    """Test deleting all tasks"""
    response = client.get('/deleteall')
    assert response.status_code == 302
    assert '/' in response.location
