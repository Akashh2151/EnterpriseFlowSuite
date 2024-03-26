from datetime import datetime
from mongoengine import Document,EmbeddedDocumentListField,StringField,DateField,ReferenceField,IntField,FloatField,EmbeddedDocument




class Product(Document):
    name = StringField(required=True)
    price = FloatField()


class Items(EmbeddedDocument):
    product = ReferenceField('Product', required=True)
    quantity = IntField(required=True)
    unitPrice = FloatField(required=True)
    subtotal = FloatField(required=True)
    totalAmount = FloatField(required=True)

class Invoices(Document):
    invoiceNumber = StringField(required=True, unique=True)
    customer = ReferenceField('customers', required=True)
    items = EmbeddedDocumentListField('Items')
    status = StringField(choices=['draft', 'issued', 'paid'], default='draft')
    paymentDueDate = DateField()
    paymentMode = StringField()
    amountPaid = FloatField()
    pendingAmount = FloatField()
    paymentTerms = StringField()
    notes = StringField()