from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Adjust as necessary
db = client["joke_app_db"]  # Replace with your database name
collection = db["jokes"]  # Replace with your collection name

# Sample documents to insert
documents = [
    {
        "_id": "68f5e4d49d543851baafb3b1",
        "content": "Why did the melon jump into the lake? It wanted to be a water-melon.",
        "author_username": "samko5sam",
    },
    # Add more documents as needed
    {
        "_id": "another_id_12345",
        "content": "What did the grape do when it got stepped on? Nothing, it just let out a little wine.",
        "author_username": "user2",
    },
    {
        "_id": "yet_another_id_67890",
        "content": "Why do seagulls fly over the ocean? Because if they flew over the bay, they'd be bagels.",
        "author_username": "user3",
    },
]

# Insert multiple documents
insert_result = collection.insert_many(documents)

# Print the inserted IDs
print("Inserted IDs:", insert_result.inserted_ids)
