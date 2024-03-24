from  mongoengine import StringField,ReferenceField,Document



class BusinessInfos(Document):
    userId = ReferenceField('Userbases', required=True)
    businessName = StringField(required=True)
    industry = StringField()
    address = StringField()
    phone = StringField()
    website = StringField()
    description = StringField()
    businessType = StringField()
    status = StringField(choices=['active', 'inactive'], default='active')



    meta = {
        'collection': 'businessinfos'  # Explicitly set the collection name
    }