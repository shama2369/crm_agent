from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId

load_dotenv()

def save_feedback(data: dict):
    """
    Save structured feedback data into MongoDB (Railway)
    under db = crm, collection = returned_cust.
    Falls back to local JSON if connection fails.
    """
    print(f"SAVE_FEEDBACK CALLED - Data type: {type(data)}")
    print(f"SAVE_FEEDBACK CALLED - Data preview: {str(data)[:200]}...")
    print(f"SAVE_FEEDBACK CALLED - Data length: {len(str(data))}")
    print(f"SAVE_FEEDBACK CALLED - First 10 chars: {repr(str(data)[:10])}")
    print(f"SAVE_FEEDBACK CALLED - Last 10 chars: {repr(str(data)[-10:])}")
    
    try:
        mongo_uri = os.getenv("MONGO_URI")

        if not mongo_uri:
            print("No MONGO_URI found, saving to local JSON file instead.")
            return save_to_json(data)

        # Connect to MongoDB (Railway)
        client = MongoClient(mongo_uri)
        db = client["crm"]                  # Database name: crm
        collection = db["returned_cust"]    # Collection name: returned_cust

        # Ensure data is dictionary - handle both dict and string inputs
        if isinstance(data, str):
            print(f"Processing string data: {data[:100]}...")
            try:
                # Try to parse as JSON first
                data = json.loads(data)
                print("JSON parsing succeeded")
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                # If it's a string representation of a dict, try conversion
                try:
                    # Handle string representations like "{'key': 'value'}"
                    # Clean the string first - remove any extra whitespace/newlines
                    cleaned_data = data.strip()
                    
                    if cleaned_data.startswith('{') and cleaned_data.endswith('}'):
                        print("Detected string dictionary format")
                        # Replace None with null for JSON parsing
                        json_str = cleaned_data.replace('None', 'null').replace("'", '"')
                        print(f"Converted JSON string: {json_str[:100]}...")
                        data = json.loads(json_str)
                        print("String-to-dict conversion succeeded")
                        print(f"Converted to dict with {len(data)} keys: {list(data.keys())[:5]}...")
                    else:
                        print("Not a string dictionary format, wrapping in raw_data")
                        data = {"raw_data": data}
                except Exception as e:
                    print(f"String-to-dict conversion failed: {e}")
                    print(f"Failed string: {repr(data[:100])}")
                    data = {"raw_data": data}
        elif isinstance(data, dict):
            # Data is already a dictionary - use it directly
            print(f"Data is already a dictionary with {len(data)} keys")
            pass
        else:
            # Unknown data type - wrap it
            data = {"raw_data": str(data)}

        # Add timestamp
        data["created_at"] = datetime.utcnow()
        
        print(f"FINAL DATA TO INSERT - Type: {type(data)}")
        print(f"FINAL DATA TO INSERT - Keys: {list(data.keys())}")
        print(f"FINAL DATA TO INSERT - Sample: {dict(list(data.items())[:3])}")
        print(f"FINAL DATA TO INSERT - Has raw_data key: {'raw_data' in data}")
        if 'raw_data' in data:
            print(f"FINAL DATA TO INSERT - raw_data value: {str(data['raw_data'])[:100]}...")

        collection.insert_one(data)
        print("Data inserted into Railway MongoDB: crm.returned_cust")

        return {"status": "saved to MongoDB", "collection": "returned_cust"}

    except Exception as e:
        print(f"MongoDB insert failed: {e}")
        return save_to_json(data)


def save_to_json(data: dict):
    """Fallback: save feedback to local JSON file if MongoDB fails"""
    try:
        os.makedirs("feedback_data", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"feedback_data/feedback_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {"status": "saved to local file", "filename": filename}

    except Exception as e:
        return {"status": "failed to save", "error": str(e)}

def get_filtered_feedback(filters):
    """Get filtered feedback data based on comprehensive filters."""
    try:
        mongo_uri = os.getenv("MONGO_URI")
        
        if not mongo_uri:
            print("No MONGO_URI found, returning empty list.")
            return []

        # Connect to MongoDB (Railway)
        client = MongoClient(mongo_uri)
        db = client["crm"]
        collection = db["returned_cust"]

        print(f"Filters received: {filters}")
        
        # Build MongoDB query
        query = {}
        
        # Search across multiple fields
        if filters.get("feedbackId"):
            search_term = filters["feedbackId"]
            query["_id"] = {"$regex": search_term, "$options": "i"}
        
        # Field-specific filters
        filter_fields = {
            "salesperson": "salesperson_name",
            "itemType": "item_type",
            "metalType": "metal_type",
            "customerIntent": "customer_intent",
            "designPreference": "design_preference",
            "customerMood": "customer_mood",
            "storeImpression": "store_impression",
            "customerSupport": "customer_support",
            "priceIssue": "reason_price",
            "sizeIssue": "reason_size"
        }
        
        for filter_key, field_name in filter_fields.items():
            value = filters.get(filter_key)
            if value:
                if value == "Empty":
                    query[field_name] = {"$in": [None, ""]}
                elif value != "All":
                    query[field_name] = value
        
        print(f"MongoDB Query: {query}")
        
        # Execute query
        feedback_data = list(collection.find(query).sort("created_at", -1))
        
        # Convert ObjectId to string for JSON serialization
        for item in feedback_data:
            item["_id"] = str(item["_id"])
        
        print(f"Retrieved {len(feedback_data)} filtered feedback records")
        return feedback_data

    except Exception as e:
        print(f"Error retrieving filtered feedback data: {e}")
        return []

def get_all_feedback():
    """Get all feedback data for the filter table."""
    try:
        mongo_uri = os.getenv("MONGO_URI")
        
        if not mongo_uri:
            print("No MONGO_URI found, returning empty list.")
            return []

        # Connect to MongoDB (Railway)
        client = MongoClient(mongo_uri)
        db = client["crm"]
        collection = db["returned_cust"]

        # Get all feedback data
        feedback_data = list(collection.find().sort("created_at", -1))
        
        # Convert ObjectId to string for JSON serialization
        for item in feedback_data:
            item["_id"] = str(item["_id"])
        
        print(f"Retrieved {len(feedback_data)} feedback records")
        return feedback_data

    except Exception as e:
        print(f"Error retrieving feedback data: {e}")
        return []

def delete_feedback_record(feedback_id: str):
    """Delete a specific feedback record."""
    try:
        mongo_uri = os.getenv("MONGO_URI")
        
        if not mongo_uri:
            print("No MONGO_URI found, cannot delete.")
            return False

        # Connect to MongoDB (Railway)
        client = MongoClient(mongo_uri)
        db = client["crm"]
        collection = db["returned_cust"]

        # First, get the record to check for image_url
        record = collection.find_one({"_id": ObjectId(feedback_id)})
        
        if not record:
            print(f"Feedback record not found: {feedback_id}")
            return False

        # Get image_url if it exists
        image_url = record.get("image_url")
        print(f"[DELETE_DB] Found record with image_url: {image_url}")
        print(f"[DELETE_DB] image_url type: {type(image_url)}")
        
        # Delete the record
        result = collection.delete_one({"_id": ObjectId(feedback_id)})
        
        if result.deleted_count > 0:
            print(f"[DELETE_DB] ✓ Deleted feedback record: {feedback_id}")
            print(f"[DELETE_DB] Returning: deleted=True, image_url={image_url}")
            
            # Return image_url if it exists, so the caller can delete the file
            return {"deleted": True, "image_url": image_url}
        else:
            print(f"[DELETE_DB] ✗ Failed to delete feedback record: {feedback_id}")
            return False

    except Exception as e:
        print(f"Error deleting feedback record: {e}")
        return False
