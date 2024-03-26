from datetime import datetime
from flask import Blueprint, jsonify, request
from wtforms import ValidationError
from mongoengine import DoesNotExist

from model.bizinfo_model import BusinessInfos
from model.customer_model import customers


cust_db=Blueprint('cust_db',__name__)

# create_customer
@cust_db.route('/training/v1/api/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        
        # Verify the business info exists
        business_info = BusinessInfos.objects(id=data.get('registeredBy')).first()
        if not business_info:
            return {'error': 'BusinessInfo not found'}, 404
        
        # Instantiate a Customer object with the provided data
        customer = customers(
            firstName=data.get('firstName'),
            lastName=data.get('lastName'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country'),
            postalCode=data.get('postalCode'),
            company=data.get('company'),
            notes=data.get('notes'),
            barcode=data.get('barcode'),
            firstVisit=datetime.strptime(data.get('firstVisit'), '%Y-%m-%d') if data.get('firstVisit') else None,
            lastVisit=datetime.strptime(data.get('lastVisit'), '%Y-%m-%d') if data.get('lastVisit') else None,
            registeredBy=business_info
        )

        # Save the Customer object to the database
        customer.save()

       # Manually prepare the customer data
        customer_data = {
            'id': str(customer.id),
            'firstName': customer.firstName,
            'lastName': customer.lastName,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'city': customer.city,
            'state': customer.state,
            'country': customer.country,
            'postalCode': customer.postalCode,
            'company': customer.company,
            'notes': customer.notes,
            'barcode': customer.barcode,
            'firstVisit': customer.firstVisit.strftime('%Y-%m-%d') if customer.firstVisit else None,
            'lastVisit': customer.lastVisit.strftime('%Y-%m-%d') if customer.lastVisit else None,
            'registeredBy': str(customer.registeredBy.id)  # Adjust based on how you serialize 'registeredBy'
        }

        return jsonify({
            'body': [customer_data],
            'message': 'Customer created successfully',
            'status': 'success',
            'statusCode': 201
        }), 201
    
    except ValidationError as ve:
        return jsonify({'body': {}, 'message': str(ve), 'status': 'error', 'statusCode': 400}), 400
    except Exception as e:
        return jsonify({'body': {}, 'message': str(e), 'status': 'error', 'statusCode': 500}), 500



# get_all_customers
@cust_db.route('/training/v1/api/customers', methods=['GET'])
def get_all_customers():
    try:
        # Fetching all customer records from the database
        customer_records = customers.objects.all()

        # Manually serializing database documents to dictionaries
        customers_json = [{
            'id': str(customer.id),  # Convert ObjectId to string
            'firstName': customer.firstName,
            'lastName': customer.lastName,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'city': customer.city,
            'state': customer.state,
            'country': customer.country,
            'postalCode': customer.postalCode,
            'company': customer.company,
            'notes': customer.notes,
            'barcode': customer.barcode,
            'firstVisit': customer.firstVisit.isoformat() if customer.firstVisit else None,
            'lastVisit': customer.lastVisit.isoformat() if customer.lastVisit else None,
            'registeredBy': str(customer.registeredBy.id) if customer.registeredBy else None  # Adjusted to handle null and fetch id
        } for customer in customer_records]

        return jsonify({'body': customers_json, 'message': 'Customers fetched successfully', 'status': 'success', 'statusCode': 200}), 200
    except Exception as e:
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500
    

@cust_db.route('/training/v1/api/customers/<string:customerId>', methods=['GET'])
def get_customer_by_id(customerId):
    try:
        # Attempt to fetch the customer by their ID
        customer = customers.objects.get(id=customerId)

        # Serialize the customer document to a dictionary
        customer_json = {
            'id': str(customer.id),
            'firstName': customer.firstName,
            'lastName': customer.lastName,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'city': customer.city,
            'state': customer.state,
            'country': customer.country,
            'postalCode': customer.postalCode,
            'company': customer.company,
            'notes': customer.notes,
            'barcode': customer.barcode,
            'firstVisit': customer.firstVisit.isoformat() if customer.firstVisit else None,
            'lastVisit': customer.lastVisit.isoformat() if customer.lastVisit else None,
            'registeredBy': str(customer.registeredBy.id) if customer.registeredBy else None
        }

        # Return the customer wrapped in a list for the array of objects requirement
        return jsonify({'body': [customer_json], 'message': 'Customer fetched successfully', 'status': 'success', 'statusCode': 200}), 200
    except customers.DoesNotExist:
        # Customer not found
        return jsonify({'body': [], 'message': 'Customer not found', 'status': 'error', 'statusCode': 404}), 404
    except Exception as e:
        # Generic error handling
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500

@cust_db.route('/training/v1/api/customers/<string:customerId>', methods=['PUT'])
def update_customer(customerId):
    try:
        # Attempt to fetch the customer by their ID
        customer = customers.objects.get(id=customerId)

        # Update the customer with the data provided in the request body, except for 'registeredBy'
        data = request.json
        registeredBy_id = data.pop('registeredBy', None)

        if registeredBy_id:
            # Attempt to fetch the BusinessInfos document by its ID
            business_info = BusinessInfos.objects(id=registeredBy_id).first()
            if not business_info:
                return jsonify({'body': [], 'message': 'BusinessInfo not found', 'status': 'error', 'statusCode': 404}), 404
            # Update the 'registeredBy' field with the fetched BusinessInfos document
            customer.registeredBy = business_info
        customer.update(**data)
        
        # Fetch the updated customer
        customer.reload()

        # Serialize the updated customer document to a dictionary
        customer_json = {
            # existing serialization code here
            'id': str(customer.id),
            'firstName': customer.firstName,
            'lastName': customer.lastName,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'city': customer.city,
            'state': customer.state,
            'country': customer.country,
            'postalCode': customer.postalCode,
            'company': customer.company,
            'notes': customer.notes,
            'barcode': customer.barcode,
            'firstVisit': customer.firstVisit.isoformat() if customer.firstVisit else None,
            'lastVisit': customer.lastVisit.isoformat() if customer.lastVisit else None,
            'registeredBy': str(customer.registeredBy.id) if customer.registeredBy else None
        }

        # Return the updated customer
        return jsonify({'body': [customer_json], 'message': 'Customer updated successfully', 'status': 'success', 'statusCode': 200}), 200
    except ValidationError as e:
        # Handle validation errors
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 400}), 400
    except DoesNotExist:
        # Handle the case where the customer does not exist
        return jsonify({'body': [], 'message': 'Customer not found', 'status': 'error', 'statusCode': 404}), 404
    except Exception as e:
        # Generic error handling
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500

@cust_db.route('/training/v1/api/customers/<string:customerId>', methods=['DELETE'])
def delete_customer(customerId):
    try:
        # Attempt to delete the customer by their ID
        customer = customers.objects.get(id=customerId)
        customer.delete()
        
        # Since the customer was successfully deleted, return a success message
        return jsonify({'body': [], 'message': 'Customer successfully deleted', 'status': 'success', 'statusCode': 204}), 200
    except DoesNotExist:
        # Handle case where the customer does not exist
        return jsonify({'body': [], 'message': 'Customer not found', 'status': 'error', 'statusCode': 404}), 404
    except ValidationError:
        # Handle case where the provided ID is invalid
        return jsonify({'body': [], 'message': 'Invalid customer ID', 'status': 'error', 'statusCode': 400}), 400
    except Exception as e:
        # Generic error handling for any other unexpected errors
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500