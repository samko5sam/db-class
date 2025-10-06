import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Database Configuration ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Use pymysql as the driver
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Item {self.name}>'

# --- Routes ---

# READ: Display all items
@app.route('/')
def index():
    # Query all items from the database, order by most recent
    items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('index.html', items=items)

# CREATE: Add a new item
@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get('name')
    description = request.form.get('description')

    if not name:
        # Optional: Add flash messaging for better user feedback
        return redirect(url_for('index'))
    
    new_item = Item(name=name, description=description)
    
    try:
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return "There was an issue adding your item."

# UPDATE: Edit an existing item (show the edit form)
@app.route('/edit/<int:item_id>')
def edit_form(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('edit.html', item=item)
    
# UPDATE: Process the form submission
@app.route('/update/<int:item_id>', methods=['POST'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.name = request.form.get('name')
    item.description = request.form.get('description')
    
    try:
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return "There was an issue updating your item."

# DELETE: Remove an item
@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item_to_delete = Item.query.get_or_404(item_id)
    
    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return "There was an issue deleting that item."


if __name__ == "__main__":
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)