from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import redis
import json
import os
from datetime import timedelta
import sys
sys.path.append('/app')
from shared.models import User, UserRole
from shared.utils import generate_id

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

# In-memory user storage for demo (use database in production)
USERS = {}

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', UserRole.RIDER.value)
    phone = data.get('phone')
    
    if email in USERS:
        return jsonify({'error': 'User already exists'}), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(
        id=generate_id(),
        email=email,
        name=name,
        role=UserRole(role),
        phone=phone
    )
    
    USERS[email] = {
        'user': user.dict(),
        'password': hashed_password.decode('utf-8')
    }
    
    return jsonify({'message': 'User created successfully', 'user': user.dict()}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user_data = USERS.get(email)
    if not user_data:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=email)
    
    # Store user session in Redis
    redis_client.setex(
        f'session:{email}',
        3600,
        json.dumps(user_data['user'])
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user_data['user']
    }), 200

@app.route('/auth/verify', methods=['GET'])
@jwt_required()
def verify():
    current_user_email = get_jwt_identity()
    user_data = redis_client.get(f'session:{current_user_email}')
    if user_data:
        return jsonify(json.loads(user_data)), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'auth'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
