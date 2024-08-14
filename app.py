#!/usr/bin/env python3

import os

import random
from datetime import date,timedelta
from flask import Flask, request, make_response, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flask_cors import CORS
from functools import wraps
from models import db, User, Product, Order, Review,OrderStatus,OrderProduct
from flask import Flask
from flask_restful import Api, Resource, reqparse
import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
from flask_mail import Message ,Mail
from flask import render_template_string



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'solar_website.db')}")

def get_mpesa_token():

    consumer_key = 'YXZhAOLvjYqmX7TkAirasXHJfTjUHHqQtIOAGXYTLjjVfvUK'
    consumer_secret = 'c6SpWnqqHckfRGGGKQt56LKdwIDrMQXeHlGs9PEiSbfGLLAmnbUjc7niS8olHtJ2'

    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # make a get request using python requests liblary
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    return r.json()['access_token']


app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False
app.config["JWT_SECRET_KEY"] = "super-secret"  
CORS(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

# load_dotenv()

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'charitywanjiku8245@gmail.com'
app.config['MAIL_PASSWORD'] = 'zmcs hkrq ohze xcxt' 
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
# resend.api_key = os.environ.get("RESEND_API_KEY")
# Decorator for Admin Access
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        if user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def generate_verification_code():
    return f"{random.randint(100000, 999999)}"

def send_email_verification(email, token):
    msg = Message(
        "Please verify your email",
        sender="charitywanjiku8245@gmail.com",  
        recipients=[email]
    )
    
    # Create HTML content with the token in bold
    html_body = render_template_string(
        f"""
        <p>Your verification code is: <strong>{token}</strong>.</p>
        <p>Please use this code to verify your email address.</p>
        """
    )
    
    msg.body = f"Your verification code is: {token}. Please use this code to verify your email address."
    msg.html = html_body
    
    try:
        mail.send(msg)
        print(f"Verification email sent to {email}.")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")



@app.route("/")
def index():
    return "<h1>RayGen Solar Solutions</h1>"

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        response = make_response(jsonify(error="Email already exists"), 422)
        return response

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password,
        role=data.get("role", "customer"),
        phone_number=data["phone_number"]
    )
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)
    
    response = make_response(jsonify(new_user_id=new_user.id, access_token=access_token), 201)
    return response

@app.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    try:
        users = User.query.all()
        response = make_response(
            jsonify([{
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "phone_number": user.phone_number
            } for user in users]), 200
        )
        return response
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        response = make_response(jsonify({"error": "Internal Server Error"}), 500)
        return response

@app.route("/users/<int:user_id>", methods=["PUT"])

def update_user(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)

    if user.email != data["email"]:
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user:
            response = make_response(jsonify(error="Email already exists"), 422)
            return response

    user.name = data["name"]
    user.email = data["email"]
    if "password" in data:
        user.password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user.role = data.get("role", user.role)
    db.session.commit()
    response = make_response(jsonify(message="User updated successfully"), 200)
    return response



@app.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    response = make_response("", 204)
    return response

@app.route("/products", methods=["POST"])
@admin_required
def create_product():
    data = request.get_json()
    print(data)  # Log incoming data
    new_product = Product(
        name=data["name"],
       
        price=data["price"],
        
        category=data["category"],
        stock_quantity=data["stock_quantity"],
        functionality =data["functionality"]
    )
    db.session.add(new_product)
    db.session.commit()
    response = make_response(jsonify(new_product_id=new_product.id), 201)
    return response




@app.route("/products", methods=["GET"])
def get_products():
    try:
        products = Product.query.all()
        response = make_response(
            jsonify([product.to_dict() for product in products]), 200
        )
        return response
    except Exception as e:
        response = make_response(jsonify({"error": "Internal Server Error"}), 500)
        return response

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    response = make_response(jsonify(product.to_dict()), 200)
    return response

@app.route('/products/<category>', methods=['GET'])
def get_products_by_category(category):
    try:
        products = Product.query.filter(Product.category.ilike(category)).all()
        print(f"Found products: {products}")  # Debug statement
        if not products:
            return jsonify({"error": "No products found for this category"}), 404
        product_data = []
        for product in products:
            product_dict = product.to_dict()
            product_data.append(product_dict)
        return jsonify(product_data), 200
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/products/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    data = request.get_json()
    product = Product.query.get_or_404(product_id)
    product.name = data["name"]
    product.image_url= data["image_url"]
    product.price = data["price"]
    product.category = data["category"]
    product.stock_quantity = data["stock_quantity"]
    product.functionality =data["functionality"]
    db.session.commit()
    response = make_response(jsonify(message="Product updated successfully"), 200)
    return response

@app.route("/products/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    response = make_response("", 204)
    return response

@app.route('/products/category', methods=['GET'])
def get_product_category():
    category = request.args.get('category')
    
    if category:
        products = Product.query.filter_by(category=category).all()
        return jsonify([product.to_dict() for product in products]), 200
    else:
        return jsonify({'error': 'Category not specified'}), 400

@app.route('/api/products/total', methods=['GET'])
def get_total_products():
    try:
        # Fetch total number of products
        total = Product.query.count()
        return jsonify({'total': total}), 200
    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error fetching total products: {e}")
        return jsonify({'error': 'An error occurred while fetching the total number of products'}), 500

 
@app.route("/orders", methods=["GET"])
@admin_required
def get_orders():
    try:
        # Query the database to get all orders
        orders = Order.query.all()
        
        # Convert orders to a list of dictionaries, now including customer name
        orders_list = [order.to_dict() for order in orders]
        
        # Prepare the response
        response = jsonify(orders_list)
        return response
    except Exception as e:
        # Handle exceptions and return an error response
        print(f"Error retrieving orders: {e}")
        response = jsonify({"error": "An error occurred while retrieving orders."})
        return response, 500


@app.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check if the user is an admin
    if user.role != "admin":
        return jsonify({"error": "Access denied"}), 403

    # Retrieve the order regardless of the user_id
    order = Order.query.get_or_404(order_id)

    response = make_response(
        jsonify(
            {
                "order_id": order.id,
                "user_id": order.user_id,
                "order_date": order.order_date.isoformat(),
                "total_price": order.total_price,
            }
        ),
        200,
    )
    return response
@app.route('/orders/status', methods=['GET'])
def get_order_status():
    order_status = request.args.get('status')  # Ensure 'status' matches the query parameter

    if order_status:
        orders = Order.query.filter_by(order_status=order_status).all()  # Use correct column name
        return jsonify([order.to_dict() for order in orders]), 200
    else:
        return jsonify({'error': 'Status not specified'}), 400

@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    try:
        # Retrieve the order by ID
        order = Order.query.get_or_404(order_id)

        # Get JSON data from the request
        data = request.json

        # Update the order fields if they are provided in the request
        if 'order_date' in data:
            order.order_date = date.fromisoformat(data['order_date'])
        if 'total_price' in data:
            order.total_price = data['total_price']
        if 'order_status' in data:
            try:
                order.order_status = OrderStatus[data['order_status'].upper()]
            except KeyError:
                return jsonify({"error": "Invalid order status."}), 400
        if 'delivery_date' in data:
            order.delivery_date = date.fromisoformat(data['delivery_date']) if data['delivery_date'] else None

        if 'order_products' in data:
            # Assuming order_products is an array of product details
            # Clear existing products
            order.order_products.clear()
            # Add new products
            for op_data in data['order_products']:
                # Assuming OrderProduct requires certain fields
                product = OrderProduct(**op_data)
                order.order_products.append(product)

        # Save the updated order to the database
        db.session.commit()

        # Return the updated order as a JSON response
        return jsonify(order.to_dict()), 200

    except KeyError as e:
        return jsonify({"error": f"Invalid key: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Value error: {str(e)}"}), 400
    except Exception as e:
        print(f"Error updating order: {e}")
        return jsonify({"error": "An error occurred while updating the order."}), 500

@app.route("/orders/<int:order_id>", methods=["DELETE"])

def delete_order(order_id):
    try:
        # Retrieve the order by ID
        order = Order.query.get_or_404(order_id)
        print(f"Attempting to delete order with ID: {order_id}")

        # Delete the order
        db.session.delete(order)
        db.session.commit()
        print(f"Order with ID: {order_id} has been deleted successfully.")

        # Return a 204 No Content response
        return make_response("", 204)
    
    except Exception as e:
        # Log the error and return an error response
        print(f"Error occurred while deleting order with ID: {order_id}: {e}")
        db.session.rollback()
        return make_response(jsonify({"error": "Order could not be deleted"}), 500)

@app.route("/login/email", methods=["POST"])
def login_user_email():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    remember_me = data.get("remember_me", False)
    
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    
    if not user.is_verified:
        return jsonify({"error": "Please verify your email before logging in."}), 403

    if bcrypt.check_password_hash(user.password, password):
        expires = timedelta(days=30) if remember_me else timedelta(hours=1)
        token = create_access_token(identity=user.id, expires_delta=expires)
        return jsonify({"token": token, "role": user.role, "success": True}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route("/login/phone", methods=["POST"])
def login_user_phone():
    data = request.get_json()
    phone = data.get("phone")
    password = data.get("password")
    
    user = User.query.filter_by(phone_number=phone).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity=user.id)
        user.token = token
        db.session.commit()
        
        return jsonify({"token": user.token, "role": user.role, "success": True}), 200
    else:
        return jsonify({"error": "Invalid phone number or password"}), 401
@app.route('/products/search', methods=['GET'])
def search_products():
    query = request.args.get('name', '')
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return jsonify([product.to_dict() for product in products])

@app.route("/reviews", methods=["GET"])
def get_all_reviews():
    try:
        reviews = Review.query.all()
        response = make_response(
            jsonify([review.to_dict() for review in reviews]), 200
        )
        return response
    except Exception as e:
        print(f"Error fetching reviews: {str(e)}")
        response = make_response(jsonify({"error": "Internal Server Error"}), 500)
        return response

@app.route("/products/<int:product_id>/reviews", methods=["GET"])
def get_product_reviews(product_id):
    reviews = db.session.query(Review, User.name).join(User, Review.user_id == User.id).filter(Review.product_id == product_id).all()
    response_data = [
        {
            "id": review.id,
            "user_id": review.user_id,
            "user_name": user_name,
            "product_id": review.product_id,
            "comments": review.comments,
            "rating": review.rating,
            "review_date": review.review_date.strftime('%Y-%m-%d')
        }
        for review, user_name in reviews
    ]
    response = make_response(jsonify(response_data), 200)
    return response
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 422

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    verification_code = generate_verification_code()
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password,
        role=data.get("role", "customer"),
        phone_number=data["phone_number"],
        verification_code=verification_code,
        is_verified=False, 
    )
    db.session.add(new_user)
    db.session.commit()

    try:
        send_email_verification(data["email"], verification_code)
        return jsonify({"message": "User created successfully. Please check your email for the verification code."}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error sending verification email: {e}")
        return jsonify({"error": "Failed to send verification email"}), 500
    
@app.route("/verify", methods=["POST"])
def verify_email():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")

    user = User.query.filter_by(email=email, verification_code=code).first()
    if user:
        user.is_verified = True
        user.verification_code = None  
        db.session.commit()
        return jsonify({"message": "Email verified successfully."}), 200
    else:
        return jsonify({"error": "Invalid verification code or email."}), 400


@app.route("/reviews", methods=["POST"])
def create_review():
    data = request.get_json()
    
    # Ensure the required fields are present
    if not all(key in data for key in ("user_id", "product_id", "comments", "rating")):
        return make_response(jsonify({"error": "Missing required fields"}), 400)
    
    # Create a new review instance
    new_review = Review(
        user_id=data["user_id"],
        product_id=data["product_id"],
        comments=data["comments"],
        rating=data["rating"],
        review_date=date.today()  # Or use data.get("review_date") if you want to accept date from request
    )
    
    # Add and commit the new review to the database
    db.session.add(new_review)
    db.session.commit()
    
    # Return the newly created review's ID as part of the response
    response = make_response(jsonify(new_review_id=new_review.id), 201)
    return response
@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully'}), 200
@app.route("/user/profile", methods=["GET"])
@jwt_required()
def user_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    response = make_response(
        jsonify(
            {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role
            }
        ),
        200,
    )
    return response
@app.route('/user/profile/update', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    try:
        user.name = data['name']
        user.phone_number = data.get('phone', user.phone_number)
        user.email = data['email']

        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update profile. Error: {str(e)}'}), 500
@app.route('/user/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not bcrypt.check_password_hash(user.password, data.get('currentPassword')):
        return jsonify({'message': 'Current password is incorrect'}), 401

    if data.get('newPassword') != data.get('confirmPassword'):
        return jsonify({'message': 'Passwords do not match'}), 400

    try:
        user.password = bcrypt.generate_password_hash(data.get('newPassword')).decode('utf-8')
        db.session.commit()

        return jsonify({'message': 'Password changed successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to change password. Error: {str(e)}'}), 500
def get_mpesa_token():

    consumer_key = 'YXZhAOLvjYqmX7TkAirasXHJfTjUHHqQtIOAGXYTLjjVfvUK'
    consumer_secret = 'c6SpWnqqHckfRGGGKQt56LKdwIDrMQXeHlGs9PEiSbfGLLAmnbUjc7niS8olHtJ2'

    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # make a get request using python requests liblary
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    return r.json()['access_token']


class MakeSTKPush(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('phone',
                        type=str,
                        required=True,
                        help="This field is required")

    parser.add_argument('amount',
                        type=str,
                        required=True,
                        help="This field is required")

    def post(self):
        """Make an STK push to Daraja API"""

        # get phone and amount from request body
        data = MakeSTKPush.parser.parse_args()

        # encode business_shortcode, online_passkey and current_time (yyyyMMhhmmss) to base64
        encode_data = b"<Business_shortcode><online_passkey><current timestamp>"
        passkey = base64.b64encode(encode_data)

        # make stk push
        try:
            # get access_token
            access_token = get_mpesa_token()

            # stk_push request url
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

            # put access_token in request headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # define request body
            request = {
                "BusinessShortCode": "174379",
                "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMTYwMjE2MTY1NjI3",
                "Timestamp": "20160216165627",
                "TransactionType": "CustomerPayBillOnline",
                "Amount": data["amount"],
                "PartyA": data["phone"],
                "PartyB": "174379",
                "PhoneNumber": data["phone"],
                "CallBackURL": "https://mydomain.com/pat",
                "AccountReference": "Test",
                "TransactionDesc": "Test"
            }

            # make request and catch response
            response = requests.post(api_url, json=request, headers=headers)

            # check response code for errors and return response
            if response.status_code > 299:
                return {
                    "success": False,
                    "message": "Sorry, something went wrong please try again later."
                }, 400

            # CheckoutRequestID = response.text['CheckoutRequestID']

            # Do something in your database e.g store the transaction or as an order
            # make sure to store the CheckoutRequestID to identify the transaction in
            # your CallBackURL endpoint.

            # return a response to your user
            return {
                "data": json.loads(response.text)
            }, 200

        except:
            # catch error and return response
            return {
                "success": False,
                "message": "Sorry something went wrong please try again."
            }, 400


# stk push path [POST request to {baseURL}/stkpush]
api.add_resource(MakeSTKPush, "/stkpush")

if __name__ == "_main_":
    app.run(debug=True, port=5000)