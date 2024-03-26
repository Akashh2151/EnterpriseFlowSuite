from datetime import datetime
from mongoengine import Document,StringField,DateTimeField,ReferenceField


class customers(Document):
    firstName=StringField(required=True)
    lastName=StringField(required=True)
    email=StringField(required=True)
    phone=StringField(required=True)
    address=StringField(required=True)
    city=StringField(required=True)
    state=StringField(required=True)
    country=StringField(required=True)
    postalCode=StringField(required=True)
    company=StringField(required=True)
    notes=StringField(required=True)
    barcode=StringField(required=True)
    firstVisit=DateTimeField(default=datetime.now)
    lastVisit=DateTimeField()
    registeredBy=ReferenceField('BusinessInfos')
