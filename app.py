#!/usr/bin/env python3

import os
import resend
import random
from datetime import date,timedelta
from flask import Flask, request, make_response, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flask_cors import CORS
from functools import wraps
from models import db, User, Product, Order, Review

# from dotenv import load_dotenv
from flask_mail import Mail, Message


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'solar_website.db')}")

app = Flask(__name__)
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

app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'cc6618a4c2436c'
app.config['MAIL_PASSWORD'] = '8578432f236d9f'
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
        sender="onesmusmwai40@gmail.com",  
        recipients=[email]
    )
    msg.body = f"Your verification code is: {token}. Please use this code to verify your email address."
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
@admin_required
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

@app.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    response = make_response(
        jsonify(
            {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            }
        ),
        200,
    )
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
        description=data["description"],
        supplier=data["supplier"]
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

@app.route("/orders", methods=["POST"])

def create_order():
    data = request.get_json()
    new_order = Order(
        user_id=data["user_id"],
        order_date=date.today(),
        total_price=data["total_price"],
    )
    db.session.add(new_order)
    db.session.commit()
    response = make_response(jsonify(new_order_id=new_order.id), 201)
    return response

@app.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    order = Order.query.get_or_404(order_id)
    if order.user_id != user_id:
        return jsonify({"error": "Access denied"}), 403
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

@app.route("/orders/<int:order_id>", methods=["PUT"])
@admin_required
def update_order(order_id):
    data = request.get_json()
    order = Order.query.get_or_404(order_id)
    order.user_id = data["user_id"]
    order.order_date = data["order_date"]
    order.total_price = data["total_price"]
    db.session.commit()
    response = make_response(jsonify(message="Order updated successfully"), 200)
    return response

@app.route("/orders/<int:order_id>", methods=["DELETE"])
@jwt_required()
def delete_order(order_id):
    user_id = get_jwt_identity()
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != user_id:
        user = User.query.get(user_id)
        if user.role != 'admin':
            return jsonify({"error": "Access denied"}), 403

    db.session.delete(order)
    db.session.commit()
    response = make_response("", 204)
    return response

@app.route("/login/email", methods=["POST"])
def login_user_email():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    remember_me = data.get("remember_me", False)
    
    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
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


if __name__ == "_main_":
    app.run(debug=True, port=5000)