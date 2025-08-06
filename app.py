from flask import Flask, render_template, request, redirect
import redis
import uuid
from datetime import datetime

app = Flask(__name__)

# Connexion Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        project_id = str(uuid.uuid4())

        r.hset(f"project:{project_id}", mapping={
            "name": name,
            "description": description,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return redirect("/")

    query = request.args.get("q", "").lower()
    keys = r.keys("project:*")
    projects = []

    for key in keys:
        data = r.hgetall(key)
        data["id"] = key.split(":")[1]
        if not query or query in data["name"].lower():
            projects.append(data)

    return render_template("index.html", projects=projects)

@app.route("/delete/<project_id>")
def delete_project(project_id):
    r.delete(f"project:{project_id}")
    return redirect("/")

@app.route("/edit/<project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    key = f"project:{project_id}"

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        r.hset(key, mapping={"name": name, "description": description})
        return redirect("/")

    project = r.hgetall(key)
    return render_template("edit.html", project=project, project_id=project_id)

if __name__ == '__main__':
    app.run(debug=True)
