from datetime import datetime
from  mongoengine import DateTimeField,StringField,connect,Document,URLField,ListField


connect(db='Ezbiz-v1',host='mongodb+srv://akashsir:EDcvSSUdbdaC6MJ1@cluster0.hmng3kx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')


class Userinfos(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(choices=['admin', 'manager', 'staff'], default='staff')
    firstName = StringField()
    lastName = StringField()
    email = StringField()
    phone = StringField()
    address = StringField()
    dateOfBirth = DateTimeField()
    gender = StringField(choices=['male', 'female', 'other'])
    profilePicture = URLField()
    department = StringField()
    employeeId = StringField()
    permissions = ListField(StringField())
    status = StringField(choices=['active', 'inactive'], default='active')
    lastLogin = DateTimeField(default=datetime.now)

