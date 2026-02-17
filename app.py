from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allows the HTML frontend to talk to Flask

# ✅ Connect to your local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pet_log_db"]
pets_collection = db["pets"]


# ── Helper ──────────────────────────────────────────────
def format_pet(pet):
    """Convert MongoDB document to a clean dict for JSON."""
    pet["_id"] = str(pet["_id"])
    return pet


# ── ROUTES ──────────────────────────────────────────────

# 📋 GET all pets
@app.route("/pets", methods=["GET"])
def get_pets():
    pets = list(pets_collection.find())
    return jsonify([format_pet(p) for p in pets])


# 🔍 GET one pet by ID
@app.route("/pets/<pet_id>", methods=["GET"])
def get_pet(pet_id):
    pet = pets_collection.find_one({"_id": ObjectId(pet_id)})
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    return jsonify(format_pet(pet))


# ➕ CREATE a new pet
@app.route("/pets", methods=["POST"])
def add_pet():
    data = request.json
    new_pet = {
        "name":       data.get("name", "Unknown"),
        "type":       data.get("type", "Unknown"),
        "age":        data.get("age", 0),
        "mood":       data.get("mood", "Happy 😊"),
        "last_activity": "None yet",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    result = pets_collection.insert_one(new_pet)
    new_pet["_id"] = str(result.inserted_id)
    return jsonify(new_pet), 201


# ✏️ UPDATE a pet (mood + last activity)
@app.route("/pets/<pet_id>", methods=["PUT"])
def update_pet(pet_id):
    data = request.json
    pets_collection.update_one(
        {"_id": ObjectId(pet_id)},
        {"$set": {
            "mood":          data.get("mood"),
            "last_activity": data.get("last_activity")
        }}
    )
    updated = pets_collection.find_one({"_id": ObjectId(pet_id)})
    return jsonify(format_pet(updated))


# 🗑️ DELETE a pet
@app.route("/pets/<pet_id>", methods=["DELETE"])
def delete_pet(pet_id):
    result = pets_collection.delete_one({"_id": ObjectId(pet_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Pet not found"}), 404
    return jsonify({"message": "Pet deleted ✅"})


# ── RUN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("🐾 Virtual Pet Log running at http://localhost:5000")
    app.run(debug=True, port=5000)
