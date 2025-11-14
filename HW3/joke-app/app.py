import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from dotenv import load_dotenv
import requests

load_dotenv()

# --- App and DB Configuration ---
app = Flask(__name__)
# It's crucial to set a secret key for session management and flashing messages
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(24)

# Connect to your local MongoDB instance
client = MongoClient(
    f"mongodb+srv://{os.environ.get('DB_NAME')}:{os.environ.get('DB_PASSWORD')}@cluster0.ciynfbx.mongodb.net/?appName=Cluster0"
)
db = client.joke_app_db  # Database name
jokes_collection = db.jokes
users_collection = db.users

# Ensure the username is unique
users_collection.create_index("username", unique=True)


# --- User Authentication Setup (Flask-Login) ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect to /login if user is not authenticated


class User(UserMixin):
    """User model for Flask-Login."""

    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]


@login_manager.user_loader
def load_user(user_id):
    """Loads a user from the DB."""
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None


def verify_hcaptcha(secret_key, response_token):
    url = "https://hcaptcha.com/siteverify"
    data = {"secret": secret_key, "response": response_token}
    response = requests.post(url, data=data)
    result = response.json()
    return result.get("success", False)


# --- Web Page Routes ---


@app.route("/")
def index():
    """Home page: Renders one initial joke."""
    # Fetch one random joke using MongoDB's aggregation pipeline
    pipeline = [{"$sample": {"size": 5}}]
    initial_jokes = list(jokes_collection.aggregate(pipeline))
    return render_template("index.html", initial_jokes=initial_jokes)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login and registration."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    site_key = os.environ.get("HCAPTCHA_SITE_KEY", "")
    if request.method == "POST":
        hcaptcha_response = request.form.get("h-captcha-response")
        if not hcaptcha_response:
            flash("Please complete the captcha.", "error")
            return redirect(url_for("login"))
        secret_key = os.environ.get("HCAPTCHA_SECRET_KEY")
        if not verify_hcaptcha(secret_key, hcaptcha_response):
            flash("Captcha verification failed. Please try again.", "error")
            return redirect(url_for("login"))
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user_data = users_collection.find_one({"username": username})

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("login"))

        if "register" in request.form:
            # --- Registration Logic ---
            if len(username) < 3 or len(username) > 50:
                flash("Username must be between 3 and 50 characters.", "error")
                return redirect(url_for("login"))

            if len(password) < 8 or len(password) > 100:
                flash("Password must be between 8 and 100 characters.", "error")
                return redirect(url_for("login"))

            if user_data:
                flash(
                    "Username already exists. Please choose another or log in.", "error"
                )
                return redirect(url_for("login"))

            hashed_password = generate_password_hash(password)
            new_user_id = users_collection.insert_one(
                {"username": username, "password": hashed_password}
            ).inserted_id

            new_user_data = users_collection.find_one({"_id": new_user_id})
            user = User(new_user_data)
            login_user(user)
            flash("Registration successful! You are now logged in.", "success")
            return redirect(url_for("index"))

        else:
            # --- Login Logic ---
            if user_data and check_password_hash(user_data["password"], password):
                user = User(user_data)
                login_user(user)
                return redirect(url_for("index"))
            else:
                flash("Invalid username or password.", "error")
                return redirect(url_for("login"))

    return render_template("login.html", site_key=site_key)


@app.route("/logout")
@login_required
def logout():
    """Logs the user out."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/post", methods=["GET", "POST"])
@login_required  # Protect this route
def post_joke():
    """Page for logged-in users to post a new joke."""
    if request.method == "POST":
        joke_contents = request.form.getlist("joke_content")
        jokes = [content.strip() for content in joke_contents if content.strip()]
        if jokes:
            joke_docs = [
                {"content": joke, "author_username": current_user.username}
                for joke in jokes
            ]
            jokes_collection.insert_many(joke_docs)
            num_jokes = len(jokes)
            if num_jokes == 1:
                flash("Your joke has been posted!", "success")
            else:
                flash(f"Your {num_jokes} jokes have been posted!", "success")
            return redirect(url_for("user_jokes", username=current_user.username))
        flash("No valid joke content provided.", "error")

    return render_template("post_joke.html")


@app.route("/user/<username>")
def user_jokes(username):
    """Shows a page with all jokes posted by a specific user."""
    # First, check if the user actually exists to provide a better error message
    user = users_collection.find_one({"username": username})
    if not user:
        flash(f'User "{username}" not found.', "error")
        return redirect(url_for("index"))

    # Fetch all jokes by this author, sorted by most recent first
    # Sorting by '_id' in descending order is a common way to get recent posts
    user_jokes_cursor = jokes_collection.find({"author_username": username}).sort(
        "_id", DESCENDING
    )
    jokes_list = list(user_jokes_cursor)

    return render_template("user_jokes.html", jokes=jokes_list, username=username)


# --- API Endpoint for Infinite Scroll ---


@app.route("/api/jokes")
def get_jokes():
    """API endpoint to fetch one random joke for the infinite scroll."""
    # This pipeline will return an empty list if the collection is empty, which is safe.
    pipeline = [{"$sample": {"size": 1}}]
    jokes = list(jokes_collection.aggregate(pipeline))

    if not jokes:
        # If no jokes are found, return an empty object with a 200 status.
        # The frontend JS already handles this gracefully.
        return jsonify({})

    joke = jokes[0]
    # Convert ObjectId to string for JSON serialization
    joke["_id"] = str(joke["_id"])

    return jsonify(joke)


@app.route("/edit_joke/<joke_id>", methods=["GET", "POST"])
@login_required
def edit_joke(joke_id):
    """Handles editing an existing joke."""
    try:
        oid = ObjectId(joke_id)
    except:
        return "Invalid Joke ID", 400

    joke = jokes_collection.find_one({"_id": oid})

    if not joke:
        flash("Joke not found.", "error")
        return redirect(url_for("index"))

    # Authorization check: only the author can edit
    if joke["author_username"] != current_user.username:
        flash("You are not authorized to edit this joke.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        updated_content = request.form.get("joke_content")
        if updated_content:
            jokes_collection.update_one(
                {"_id": oid}, {"$set": {"content": updated_content}}
            )
            flash("Joke updated successfully!", "success")
            return redirect(url_for("user_jokes", username=joke["author_username"]))
        else:
            flash("Joke content cannot be empty.", "error")

    return render_template("edit_joke.html", joke=joke)


@app.route("/delete_joke/<joke_id>", methods=["POST"])
@login_required
def delete_joke(joke_id):
    """Handles deleting a joke."""
    try:
        oid = ObjectId(joke_id)
    except:
        return "Invalid Joke ID", 400

    joke = jokes_collection.find_one({"_id": oid})

    if not joke:
        flash("Joke not found.", "error")
        return redirect(url_for("index"))

    # Authorization check: only the author can delete
    if joke["author_username"] != current_user.username:
        flash("You are not authorized to delete this joke.", "error")
        return redirect(url_for("index"))

    jokes_collection.delete_one({"_id": oid})
    flash("Joke deleted successfully.", "success")
    return redirect(url_for("user_jokes", username=joke["author_username"]))


if __name__ == "__main__":
    app.run(debug=True)
