from flask import Flask, render_template, request, redirect, url_for, jsonify
from bson import ObjectId
from pymongo import MongoClient
import os
from flask import abort

# Configuration and Initialization
app = Flask(__name__)

# App Constants
APP_TITLE = "TODO APP"
APP_HEADING = "TODO APP"

#print(os.getenv("MONGO_URI"))


# Environment Variables for Secure Database URI
DB_URI = os.getenv("MONGO_URI", "mongodb+srv://hadolesarvesh031:bU48XDP07sqVLnAJ@todoflaskmongodb.jqefh.mongodb.net/?retryWrites=true&w=majority&appName=todoflaskmongodb")
DB_NAME = os.getenv("DB_NAME", "mymongodb")

# Database Setup
client = MongoClient(DB_URI)
db = client[DB_NAME]
todos = db.todo

# Helper Functions
def redirect_url():
    """Get the appropriate redirection URL."""
    return request.args.get('next') or request.referrer or url_for('list_tasks')


def get_task_by_id(task_id):
    """Retrieve a task by ObjectId."""
    try:
        return todos.find_one({"_id": ObjectId(task_id)})
    except Exception as e:
        print(f"Error retrieving task by ID: {e}")
        abort(500, description="Internal Server Error")

# Routes
@app.route("/")
@app.route("/list")
def list_tasks():
    """Display all tasks."""
    todos_list = todos.find()
    return render_template('index.html', active_tab="list", todos=todos_list, t=APP_TITLE, h=APP_HEADING)

@app.route("/uncompleted")
def uncompleted_tasks():
    """Display uncompleted tasks."""
    todos_list = todos.find({"done": "no"})
    return render_template('index.html', active_tab="uncompleted", todos=todos_list, t=APP_TITLE, h=APP_HEADING)

@app.route("/completed")
def completed_tasks():
    """Display completed tasks."""
    todos_list = todos.find({"done": "yes"})
    return render_template('index.html', active_tab="completed", todos=todos_list, t=APP_TITLE, h=APP_HEADING)

@app.route("/done")
def toggle_task_status():
    """Toggle task completion status."""
    task_id = request.values.get("_id")
    
    # Validate task ID
    if not ObjectId.is_valid(task_id):
        return "Invalid task ID", 404

    task = get_task_by_id(task_id)
    if not task:
        return "Task not found", 404

    new_status = "no" if task["done"] == "yes" else "yes"
    todos.update_one({"_id": ObjectId(task_id)}, {"$set": {"done": new_status}})
    return redirect(redirect_url())



@app.route("/action", methods=['POST'])
def add_task():
    """Add a new task."""
    task_data = {
        "name": request.values.get("name"),
        "desc": request.values.get("desc"),
        "date": request.values.get("date"),
        "pr": request.values.get("pr"),
        "done": "no"
    }
    todos.insert_one(task_data)
    return redirect("/list")

@app.route("/remove")
def remove_task():
    """Delete a task."""
    task_id = request.values.get("_id")
    if get_task_by_id(task_id):
        todos.delete_one({"_id": ObjectId(task_id)})
    return redirect("/")

@app.route("/update")
def update_task():
    """Render task update page."""
    task_id = request.values.get("_id")
    task = get_task_by_id(task_id)
    return render_template('update.html', tasks=[task], h=APP_HEADING, t=APP_TITLE)

@app.route("/action3", methods=['POST'])
def perform_update():
    """Update an existing task."""
    task_id = request.values.get("_id")
    updated_data = {
        "name": request.values.get("name"),
        "desc": request.values.get("desc"),
        "date": request.values.get("date"),
        "pr": request.values.get("pr")
    }
    todos.update_one({"_id": ObjectId(task_id)}, {"$set": updated_data})
    return redirect("/")

@app.route("/search", methods=['GET'])
def search_task():
    """Search tasks."""
    search_key = request.values.get("key")
    search_ref = request.values.get("refer")
    search_query = {search_ref: ObjectId(search_key)} if search_key == "_id" else {search_ref: search_key}
    results = todos.find(search_query)
    return render_template('searchlist.html', todos=results, t=APP_TITLE, h=APP_HEADING)

@app.route("/deleteall")
def delete_all_tasks():
    """Delete all tasks."""
    todos.delete_many({})
    return redirect("/")

# Entry Point
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000, use_reloader=True)
