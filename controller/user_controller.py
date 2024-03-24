from datetime import datetime, timedelta
import hashlib
import re
import uuid
from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import generate_password_hash
from mongoengine.errors import NotUniqueError, ValidationError
import jwt
from model.user_model import Userinfos
 

usermanagment=Blueprint('usermanagment',__name__)
#create user
@usermanagment.route('/training/v1/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json

        # Basic Validation for required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({'body': {}, 'message': 'Username and Password are required', 'status': 'error', 'statusCode': 400}), 400

        # You might want to validate email and phone uniqueness as well here

        # Hashing the password before saving to database
        hashed_password = generate_password_hash(data['password'], method='sha256')
       
         # Parse dateOfBirth from ISO 8601 string to datetime
        date_of_birth = None
        if data.get('dateOfBirth')                                                                 :
            try:
                date_of_birth = datetime.fromisoformat(data['dateOfBirth'].rstrip('Z'))  # Remove potential 'Z' timezone indicator
            except ValueError:
                return jsonify({'body': {}, 'message': 'Invalid dateOfBirth format. Use ISO 8601 format: YYYY-MM-DDTHH:MM:SS', 'status': 'error', 'statusCode': 400}), 400
     
        # Creating the user
        user = Userinfos(
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

        user.save()
        user_data = {
            'id': str(user.id),
            'username': user.username,
            'role': user.role,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
            'dateOfBirth': user.dateOfBirth.isoformat() if user.dateOfBirth else None,
            'gender': user.gender,
            'profilePicture': user.profilePicture,
            'department': user.department,
            'employeeId': user.employeeId,
            'permissions': user.permissions,
            'status': user.status,
            'lastLogin': user.lastLogin.isoformat() if user.lastLogin else None
        }
        users_array = [user_data]
        return jsonify({'body': users_array, 'message': 'User created successfully', 'status': 'success', 'statusCode': 201}), 201

    except NotUniqueError:
        return jsonify({'body': {}, 'message': 'Username, email or phone already exists', 'status': 'error', 'statusCode': 400}), 400
    except ValidationError as e:
        # Handle other validation errors
        return jsonify({'body': {}, 'message': str(e), 'status': 'error', 'statusCode': 400}), 400
    except Exception as e:
        # Catch-all for any other errors
        return jsonify({'body': {}, 'message': 'Server Error: ' + str(e), 'status': 'error', 'statusCode': 500}), 500


# get userdetail
@usermanagment.route('/training/v1/api/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = Userinfos.objects(id=user_id).only('username', 'role', 'firstName', 'lastName', 'email', 'phone', 'address', 'dateOfBirth', 'gender', 'profilePicture', 'department', 'employeeId', 'permissions', 'status', 'lastLogin').first()
        if not user:
            return jsonify({'body': [], 'message': 'User not found', 'status': 'error', 'statusCode': 404}), 404

        user_data = user.to_mongo().to_dict()
        user_data.pop('password', None)  # Exclude the password field
        user_data['id'] = str(user_data['_id'])  # Convert ObjectId to string
        del user_data['_id']  # Remove the original ObjectId

        # Wrapping the single user_data dictionary in a list to return an array of one object
        return jsonify({'body': [user_data], 'message': 'User retrieved successfully', 'status': 'success', 'statusCode': 200}), 200
    except Exception as e:
        return jsonify({'body': {}, 'message': 'Server Error: ' + str(e), 'status': 'error', 'statusCode': 500}), 500

# update user deteails
@usermanagment.route('/training/v1/api/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = Userinfos.objects(id=user_id).first()
        if not user:
            return jsonify({'body': [], 'message': 'User not found', 'status': 'error', 'statusCode': 404}), 404
        
        data = request.json
        for field in data:
            if field == 'dateOfBirth':
                # Parse the 'dateOfBirth' from the string to a datetime object
                try:
                    data[field] = datetime.fromisoformat(data[field].rstrip('Z'))  # Adjust for timezone if necessary
                except ValueError:
                    return jsonify({'body': [], 'message': 'Invalid date format for dateOfBirth. Please use ISO 8601 format.', 'status': 'error', 'statusCode': 400}), 400
            
            # Update the user's attributes except the password
            if hasattr(user, field) and field != 'password':
                setattr(user, field, data[field])

        user.save()
        user_data = user.to_mongo().to_dict()
        user_data.pop('password', None)  # Exclude the password field
        user_data['id'] = str(user_data['_id'])
        del user_data['_id']  # Clean up the response

        # Wrapping the user_data dictionary in a list to maintain the array of objects response format
        return jsonify({'body': [user_data], 'message': 'User updated successfully', 'status': 'success', 'statusCode': 200}), 200
    except ValidationError as e:
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 400}), 400
    except Exception as e:
        return jsonify({'body': [], 'message': 'Server Error: ' + str(e), 'status': 'error', 'statusCode': 500}), 500


# delete user 
@usermanagment.route('/training/v1/api/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = Userinfos.objects(id=user_id).first()
        if not user:
            return jsonify({'body': [], 'message': 'User not found','status': 'error','statusCode': 404}),200

        user_id_str = str(user.id)  # Store user ID for response before deletion
        user.delete()

        # Successful deletion response with an empty object in the array
        # This indicates successful deletion while keeping the array structure.
        # Including the deleted user's ID might be useful for client-side reference.
        return jsonify({'body': [{'id': user_id_str}],'message': 'User deleted successfully','status': 'success','statusCode': 204 }), 200
    except Exception as e:
        # Server error response, maintains empty array for consistency
        return jsonify({'body': [],'message': f'Server Error: {e}','status': 'error','statusCode': 500}), 500


#listof all user 
@usermanagment.route('/training/v1/api/users', methods=['GET'])
def list_users():
    try:
        users = Userinfos.objects().exclude('password')  # Exclude password field from the response
        user_list = []
        for user in users:
            user_dict = user.to_mongo().to_dict()
            user_dict['_id'] = str(user_dict['_id'])  # Convert ObjectId to string
            if 'dateOfBirth' in user_dict:  # Check if 'dateOfBirth' exists and is not None
                user_dict['dateOfBirth'] = user_dict['dateOfBirth'].isoformat() if user_dict['dateOfBirth'] else None
            user_list.append(user_dict)
        
        return jsonify({'body': user_list, 'message': 'Users retrieved successfully', 'status': 'success', 'statusCode': 200}), 200
    except Exception as e:
        return jsonify({'body': [],'message': f'An error occurred: {str(e)}','status': 'error','statusCode': 500}), 500


# serch users
@usermanagment.route('/training/v1/api/users/search', methods=['POST'])
def search_users():
    try:
        search_criteria = request.json
        query = {}

        # Build query based on search criteria
        if 'username' in search_criteria:
            query['username'] = search_criteria['username']
        if 'role' in search_criteria:
            query['role'] = search_criteria['role']
        if 'department' in search_criteria:
            query['department'] = search_criteria['department']

        # Perform search
        users = Userinfos.objects(__raw__=query).exclude('password')  # Exclude password field

        # Prepare response
        user_list = []
        for user in users:
            user_dict = user.to_mongo().to_dict()
            user_dict['id'] = str(user_dict['_id'])  # Convert ObjectId to string
            del user_dict['_id']  # Remove the original ObjectId
            user_list.append(user_dict)

        return jsonify({'body': user_list, 'message': 'Users retrieved successfully', 'status': 'success', 'statusCode': 200}), 200
    except Exception as e:
        return jsonify({'body': [], 'message': 'Server Error: ' + str(e), 'status': 'error', 'statusCode': 500}), 500



@usermanagment.route('/training/v1/api/users/logout', methods=['POST'])
def logout_user():
    # Example assumes the use of Flask sessions or an equivalent mechanism
    # Adjust according to your authentication/session management approach
    try:
        auth_token = request.headers.get('Authorization')
        if auth_token:
            # Here you would invalidate the token. The specifics of this step depend on how your tokens are managed.
            # If using JWT, for example, you might add the token to a blocklist, or simply rely on the token's expiration.
            # This is a placeholder for the logic to invalidate the token.
            # invalidate_token(auth_token)  # This is a placeholder function. Implement according to your setup.

            # If using Flask sessions, you might do something like:
            # session.pop('user_id', None)  # Assuming 'user_id' is stored in session on login

            return jsonify({'message': 'Logged out successfully', 'status': 'success', 'statusCode': 200}), 200
        else:
            return jsonify({'message': 'Authorization token is missing', 'status': 'error', 'statusCode': 401}), 401
    except Exception as e:
        return jsonify({'message': 'Server Error: ' + str(e), 'status': 'error', 'statusCode': 500}), 500
    



# @usermanagment.route('/training/v1/api/users/login', methods=['POST'])
# def login():
#     credentials = request.json
#     username = credentials.get('username')
#     password = credentials.get('password')
    
#     # Dummy check for username and password
#     # Replace with actual authentication logic
#     user = Userinfos.objects(username=username).first()
#     if user and user.password == password:  # This is insecure; use hashed passwords in production
#         # Generate token (placeholder logic)
#         token = "fake-token-for-username-" + username
#         return jsonify({'body': [{'token': token}], 'message': 'Login successful', 'status': 'success', 'statusCode': 200}), 200
#     else:
#         return jsonify({'body': [], 'message': 'Invalid credentials', 'status': 'error', 'statusCode': 401}), 401
    
