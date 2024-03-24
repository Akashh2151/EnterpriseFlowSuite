from flask import Blueprint, request, jsonify
from mongoengine import DoesNotExist
from bson import ObjectId
from wtforms import ValidationError

from model.auth_model import Userbases
from model.bizinfo_model import BusinessInfos


business_info_bp = Blueprint('business_info', __name__)
@business_info_bp.route('/training/v1/api/business-info', methods=['POST'])
def create_business_info():
    try:
        userId = request.args.get('userId')
        if not userId:
            return jsonify({'body': [], 'message': 'UserId query parameter is required', 'status': 'error', 'statusCode': 400}),200

        user = Userbases.objects.get(id=userId)  # Validates user existence

        data = request.get_json()
        required_fields = ['businessName', 'industry', 'address', 'phone', 'website', 'description']

        if not all(field in data for field in required_fields):
            return jsonify({'body': [], 'message': 'Missing required fields.', 'status': 'error', 'statusCode': 400}),200

        # Create new BusinessInfo object and save it
        businessinfos = BusinessInfos(userId=user, **{field: data.get(field, '') for field in required_fields}, businessType=data.get('businessType', ''), status=data.get('status', 'active'))
        businessinfos.save()

        # Prepare the response data
        business_info_data = {
            'id': str(businessinfos.id),
            'userId': str(businessinfos.userId.id),
            'businessName': businessinfos.businessName,
            'industry': businessinfos.industry,
            'address': businessinfos.address,
            'phone': businessinfos.phone,
            'website': businessinfos.website,
            'description': businessinfos.description,
            'businessType': businessinfos.businessType,
            'status': businessinfos.status,
        }

        return jsonify({
            'body': [business_info_data],
            'message': 'Business information created successfully',
            'status': 'success',
            'statusCode': 201
        }),200

    except DoesNotExist:
        return jsonify({'body': [], 'message': 'User does not exist', 'status': 'error', 'statusCode': 404}),404
    except ValidationError as ve:
        return jsonify({'body': [], 'message': str(ve), 'status': 'error', 'statusCode': 400}),400
    except Exception as e:
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}),500
    


@business_info_bp.route('/training/v1/api/business-info/user/<userId>', methods=['GET'])
def get_business_info_by_user(userId):
    try:
        # Attempt to retrieve all business information associated with the given userId
        business_infos = BusinessInfos.objects(userId=userId)

        if not business_infos:
            return jsonify({'body': [], 'message': 'No business information found for the provided user ID', 'status': 'error', 'statusCode': 404}),200

        # Format each business info object for response
        business_infos_data = [{
            'id': str(info.id),
            'userId': str(info.userId.id),
            'businessName': info.businessName,
            'industry': info.industry,
            'address': info.address,
            'phone': info.phone,
            'website': info.website,
            'description': info.description,
            'businessType': info.businessType,
            'status': info.status,
        } for info in business_infos]

        return jsonify({
            'body': business_infos_data,
            'message': 'Business information retrieved successfully',
            'status': 'success',
            'statusCode': 200
        }),200

    except DoesNotExist:
        return jsonify({'body': [], 'message': 'User does not exist', 'status': 'error', 'statusCode': 404}),404
    except Exception as e:
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}),500
    
    
@business_info_bp.route('/training/v1/api/business-info/<infoId>', methods=['PUT'])
def update_business_info(infoId):
    try:
        data = request.get_json()
        business_info = BusinessInfos.objects.get(id=infoId)

        for field, value in data.items():
            if hasattr(business_info, field):
                setattr(business_info, field, value)
                
        business_info.save()

        updated_info_data = {
                            'id': str(business_info.id),
                            'userId': str(business_info.userId.id), 
                            'businessName': business_info.businessName, 
                            'industry': business_info.industry, 
                            'address': business_info.address, 
                            'phone': business_info.phone, 
                            'website': business_info.website, 
                            'description': business_info.description, 
                            'businessType': business_info.businessType, 
                            'status': business_info.status
                            }
        
        return jsonify({'body': [updated_info_data], 'message': 'Business information updated successfully', 'status': 'success', 'statusCode': 200}),200
    except DoesNotExist:
        return jsonify({'body': [], 'message': 'Business information not found with the provided ID', 'status': 'error', 'statusCode': 404}),404
    except ValidationError as ve:
        return jsonify({'body': [], 'message': str(ve), 'status': 'error', 'statusCode': 400}),400
    except Exception as e:
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}),500
    


@business_info_bp.route('/training/v1/api/business-info/<infoId>', methods=['DELETE'])
def delete_business_info(infoId):
    try:
        business_info = BusinessInfos.objects.get(id=infoId)
        business_info.delete()
        return jsonify({'body': [], 'message': 'Business information deleted successfully', 'status': 'success', 'statusCode': 204}), 200
    except DoesNotExist:
        return jsonify({'body': [], 'message': 'Business information not found with the provided ID', 'status': 'error', 'statusCode': 404}),404
    except Exception as e:
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}),500