import hashlib
import uuid
from flask import request, jsonify
from flask_smorest import Blueprint

blp = Blueprint('fingerprint', __name__, description="Fingerprint API")

# Simulated storage (Replace this with a database or Redis)
fingerprint_store = {}

def generate_fingerprint():
    """Generates a fingerprint using user-agent and IP"""
    user_agent = request.headers.get('User-Agent', '')
    ip_address = request.remote_addr or ''
    raw_data = f"{user_agent}|{ip_address}"
    
    return hashlib.sha256(raw_data.encode()).hexdigest()

@blp.route('/fingerprint', methods=['POST'])
def store_fingerprint():
    """Stores fingerprint server-side and returns a session ID"""
    
    fingerprint = generate_fingerprint()
    
    # Check if fingerprint is already stored
    for session_id, stored_fingerprint in fingerprint_store.items():
        if stored_fingerprint == fingerprint:
            return jsonify({"session_id": session_id}), 200

    # Generate a new session ID for the fingerprint
    session_id = str(uuid.uuid4())
    fingerprint_store[session_id] = fingerprint

    return jsonify({"session_id": session_id}), 201

@blp.route('/fingerprint', methods=['GET'])
def check_fingerprint():
    """Retrieves fingerprint based on session ID"""
    
    session_id = request.headers.get("Authorization")
    
    if not session_id or session_id not in fingerprint_store:
        return jsonify({"error": "Invalid session"}), 401
    
    return jsonify({"session_id": session_id})
