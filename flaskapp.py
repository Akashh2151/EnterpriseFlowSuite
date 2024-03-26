from flask import Flask, jsonify
from controller.user_controller import usermanagment
from controller.auth_controller import auth_bp
from controller.bizinfo_controller import business_info_bp
from controller.customer_controller import cust_db



app=Flask(__name__)
app.config['SECRET_KEY'] = '98c5bc0a178ff2d6c0c1471c6f3dc5e4'
app.register_blueprint(usermanagment)
app.register_blueprint(auth_bp)
app.register_blueprint(business_info_bp)
app.register_blueprint(cust_db)


@app.route('/')
def hellow_world():
    return jsonify({'message':'hellow team!'})


if __name__=='__main__':
    app.run(debug=True)