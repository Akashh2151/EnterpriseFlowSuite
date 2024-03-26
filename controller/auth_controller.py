from datetime import datetime, timedelta
import hashlib
import re
import uuid
from flask import Blueprint, current_app, jsonify, request
import jwt

from utilities.validators import password_regex,email_regex,phone_number
from model.auth_model import Userbases


auth_bp = Blueprint('auth', __name__)
          
@auth_bp.route('/v1/api/users/register', methods=['POST'])
def register_step1():
    try:
        data = request.json
        username = data.get('username')
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')
        # confirmPassword=data.get('confirmPassword')
        # print(data)

        # Check if the email or mobile is already registered
        if Userbases.objects(email=email).first() or Userbases.objects(phone=phone).first():
            response = {"body": {}, "status": "error", "statusCode": 409, "message": 'Email or mobile is already registered'}
            return jsonify(response),200
        
        # if password != confirmPassword:
        #     response = {"body": {}, "status": "error", "statusCode": 400, "message": 'Password and confirm password do not match'}
        #     return jsonify(response),200

        # Validate required fields
        required_fields = [username, email, password, phone]
        if not all(required_fields):
            response = {"body": {}, "status": "error", "statusCode": 400, "message": 'All required fields must be provided'}
            return jsonify(response), 200
        
        # Validate password and email format
        if not re.match(password_regex, password):
            response = {'body':  {}, 'status': 'error', 'statusCode': 422, 'message': 'Password must be at least 8 to 16 characters long'}
            return jsonify(response),200

        if not re.match(email_regex, email):
            response = {'body':  {}, 'status': 'error', 'statusCode': 422, 'message': 'Email requirement not met'}
            return jsonify(response),200
        
        if not re.match(phone_number,phone):
            response = {'body': {}, 'status': 'error', 'statusCode': 422, 'message': 'Mobile number must be exactly 10 digits long and should only contain numeric characters.'}
            return jsonify(response),200
 
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Parse dateOfBirth from ISO 8601 string to datetime
        date_of_birth = None
        if data.get('dateOfBirth'):
            try:
                date_of_birth = datetime.fromisoformat(data['dateOfBirth'].rstrip('Z'))  # Remove potential 'Z' timezone indicator
            except ValueError:
                return jsonify({'body': {}, 'message': 'Invalid dateOfBirth format. Use ISO 8601 format: YYYY-MM-DDTHH:MM:SS', 'status': 'error', 'statusCode': 400}), 400
     
     
        # Create the User object
        user = Userbases(
            username=data['username'],
            password=hashed_password,
            role=data.get('role', 'staff'),  # Defaults to 'staff' if not provided
            firstName=data.get('firstName'),
            lastName=data.get('lastName'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            dateOfBirth=date_of_birth,  # Ensure this is in a proper datetime format
            gender=data.get('gender'),
            profilePicture=data.get('profilePicture'),
            department=data.get('department'),
            employeeId=data.get('employeeId'),
            permissions=data.get('permissions', []),
            status=data.get('status', 'active'),  # Defaults to 'active' if not provided
            lastLogin=datetime.now()
        )

        # Save the user to the database
        user.save()

        response = {"body": {}, "status": "success", "statusCode": 201, "message": 'Registration successfully'}
        return jsonify(response), 200

    except Exception as e:
        response = {"body": {}, "status": "error", "statusCode": 500, "message": str(e)}
        return jsonify(response), 500







# EXPECTED_ENCRYPTION_KEY = "9f8b47de-5c1a-4a6b-8d92-d67c43f7a6c4"
# # login route
@auth_bp.route('/v1/api/users/login', methods=['POST'])
def login():
   # Extracting the token from the Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.lower().startswith('bearer'):
        # The request contains a Bearer token, attempt to decode it
        token = auth_header[7:]
        try:
            decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            return jsonify({'body':{},'decoded_token': decoded, 'message': "Token decoded successfully", "status": "success", "statusCode": 200}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'body':{},'message': "The token is expired", "status": "error", "statusCode": 401}), 200
        except jwt.InvalidTokenError:
            return jsonify({'body':{},'message': "Invalid token", "status": "error", "statusCode": 401}), 200
        except Exception as e:
            return jsonify({'body':{},'message': str(e),'status': 'error','statusCode': 500}), 500
        
     # Extract the custom encryption key from the request headers
    # encryption_key = request.headers.get('X-Custom-Encryption-Key')

    # Verify the encryption key
    # if encryption_key != EXPECTED_ENCRYPTION_KEY:
    #     return jsonify({'body':{},'message': "Invalid or missing encryption key", "status": "error", "statusCode": 401}), 200

    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if email is None or password is None:
            return jsonify({'body':{},'message': 'Email and password are required', 'status': 'error', 'statusCode': 400}), 200

        # Replace this with your actual database lookup
        user = Userbases.objects(email=email).first()

        if user:
            provided_password_hash = hashlib.sha256(password.encode()).hexdigest()
            if provided_password_hash == user.password:
                # Set short expiration for the token
                exp_time = datetime.utcnow() + timedelta(minutes=1)
                payload = {
                            'sub': '1',
                            'jti': str(uuid.uuid4()),
                            'userId': str(user.id),
                            'exp':  exp_time,
                            'type': 'access',
                            'fresh': True
                }

                token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

                userinfo={
                       "name":user.username,
                        "mobile":user.phone,   
                        'identity': user.email,
                        'accessToken': token
                }

                return jsonify({
                    "body": userinfo,
                    'message': 'Login successfully',
                    'status': 'success',
             
                    'expires': exp_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'statusCode': 200
                }), 200
            else:
                return jsonify({'body':{},'message': 'Incorrect password', 'status': 'error', 'statusCode': 401}), 200
        else:
            return jsonify({'body':{},'message': 'User not found', 'status': 'error', 'statusCode': 404}), 200

    except Exception as e:
        return jsonify({'body':{},'message': str(e),'status': 'error','statusCode': 500}), 500
 
 