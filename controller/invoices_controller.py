import json
import logging
from flask import Blueprint, jsonify, request

from model.customer_model import customers
from model.invoices_model import Invoices, Items, Product


invoice_db = Blueprint('invoice_db', __name__)
@invoice_db.route('/v1/api/invoices', methods=['POST'])
def create_invoice():
    data = request.json
    
    if not data.get('userId'):
        return jsonify({'body': [], 'message': 'UserId query parameter is required', 'status': 'error', 'statusCode': 400}), 400
   
 

    try:
        customer = customers.objects(id=data['customer']).first()
        if not customer:
            return jsonify({'body': [], 'message': 'Customer not found', 'status': 'error', 'statusCode': 404}), 404
        
        items = []
        for item_data in data['items']:
            product = Product.objects(id=item_data['product']).first()
            if not product:
                continue  # Here you might want to handle the error instead of continuing
            item = Items(
                product=product,
                quantity=item_data['quantity'],
                unitPrice=item_data['unitPrice'],
                subtotal=item_data['subtotal'],
                totalAmount=item_data['totalAmount']
            )
            items.append(item)
            print(item)
        
        invoice = Invoices(
            invoiceNumber=data['invoiceNumber'],
            customer=customer,
            items=items,
            status=data.get('status', 'draft'),
            paymentDueDate=data.get('paymentDueDate'),
            paymentMode=data.get('paymentMode'),
            amountPaid=data.get('amountPaid'),
            pendingAmount=data.get('pendingAmount'),
            paymentTerms=data.get('paymentTerms'),
            notes=data.get('notes')
        )
        invoice.save()
        
        # Customizing the response to include detailed items info
        items_response = [{
            "product": str(item.product.id),
            "quantity": item.quantity,
            "unitPrice": item.unitPrice,
            "subtotal": item.subtotal,
            "totalAmount": item.totalAmount
        } for item in items]
        
        invoice_response = {
            "invoiceNumber": invoice.invoiceNumber,
            "customer": str(invoice.customer.id),
            "items": items_response,
            "status": invoice.status,
            "paymentDueDate": invoice.paymentDueDate,
            "paymentMode": invoice.paymentMode,
            "amountPaid": invoice.amountPaid,
            "pendingAmount": invoice.pendingAmount,
            "paymentTerms": invoice.paymentTerms,
            "notes": invoice.notes
        }
    
        return jsonify({'body': [invoice_response], 'message': 'Invoice created successfully', 'status': 'success', 'statusCode': 201}), 201
    except Exception as e:
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500
    


@invoice_db.route('/v1/api/invoices', methods=['GET'])
def get_all_invoices():
    userId = request.args.get('userId')
    if not userId:
        return jsonify({'body': [], 'message': 'UserId query parameter is required', 'status': 'error', 'statusCode': 400}), 400
    
    # Fetch all invoices logic
    # For simplicity, this fetches all invoices without user filtering
    invoices = Invoices.objects()
    invoices_json = [json.loads(invoice.to_json()) for invoice in invoices]
    return jsonify({'body': invoices_json, 'message': 'Invoices retrieved successfully', 'status': 'success', 'statusCode': 200}), 200


@invoice_db.route('/v1/api/invoices/<invoiceId>', methods=['GET'])
def get_invoice_by_id(invoiceId):
    userId = request.args.get('userId')
    if not userId:
        return jsonify({'body': [], 'message': 'UserId query parameter is required', 'status': 'error', 'statusCode': 400}), 400
    
    try:
        invoice = Invoices.objects(id=invoiceId).first()
        if not invoice:
            return jsonify({'body': [], 'message': 'Invoice not found', 'status': 'error', 'statusCode': 404}), 404
        return jsonify({'body': [json.loads(invoice.to_json())], 'message': 'Invoice retrieved successfully', 'status': 'success', 'statusCode': 200}), 200
    except Exception as e:
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500
    


@invoice_db.route('/v1/api/invoices/<string:invoiceId>', methods=['PUT'])
def update_invoice(invoiceId):
    if not request.json:
        return jsonify({'body': [], 'message': 'Request body is missing', 'status': 'error', 'statusCode': 400}), 400

    try:
        # Retrieve the invoice to update
        invoice = Invoices.objects(id=invoiceId).first()
        if not invoice:
            return jsonify({'body': [], 'message': 'Invoice not found', 'status': 'error', 'statusCode': 404}), 404

        # Extract fields from request body
        data = request.json
        fields_to_update = ['invoiceNumber', 'customerId', 'items', 'totalAmount', 'status', 'paymentDueDate', 'paymentTerms', 'notes']
        for field in fields_to_update:
            if field in data:
                setattr(invoice, field, data[field])
                
        # Update and save invoice
        invoice.save()

        return jsonify({'body': [json.loads(invoice.to_json())], 'message': 'Invoice updated successfully', 'status': 'success', 'statusCode': 200}), 200
    except Exception as e:
        # Handle unexpected errors
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500






@invoice_db.route('/v1/api/invoices/<string:invoiceId>', methods=['DELETE'])
def delete_invoice(invoiceId):
    try:
        invoice = Invoices.objects(id=invoiceId).first()
        if not invoice:
            return jsonify({'body': [], 'message': 'Invoice not found', 'status': 'error', 'statusCode': 404}), 404
        
        invoice.delete()
        return jsonify({'body': [], 'message': 'Invoice deleted successfully', 'status': 'success', 'statusCode': 200}), 200
    except Exception as e:
        logging.error(f"Error deleting invoice: {str(e)}")
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500
    


@invoice_db.route('/v1/api/invoices/<string:invoiceId>/issue', methods=['PUT'])
def issue_invoice(invoiceId):
    try:
        invoice = Invoices.objects(id=invoiceId).first()
        if not invoice:
            return jsonify({'body': [], 'message': 'Invoice not found', 'status': 'error', 'statusCode': 404}), 404

        invoice.update(status='issued')
        return jsonify({'body': [], 'message': 'Invoice issued successfully', 'status': 'success', 'statusCode': 200}), 200
    except Exception as e:
        logging.error(f"Error issuing invoice: {str(e)}")
        return jsonify({'body': [], 'message': str(e), 'status': 'error', 'statusCode': 500}), 500