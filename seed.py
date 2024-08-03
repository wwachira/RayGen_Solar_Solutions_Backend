from app import app, db;
from models import User, Product, Order, OrderProduct, Review;
from datetime import date;

with app.app_context():
    db.drop_all()
    db.create_all()


    users = [
        User(fullname="Alice Smith", email="alice@example.com", password="password123", role="customer", phone_number="1234567890"),
        User(fullname="Bob Johnson", email="bob@example.com", password="password123", role="admin", phone_number="0987654321"),
        User(fullname="Charlie Brown", email="charlie@example.com", password="password123", role="customer"),
    ]

    products = [
        Product(name="Solar Panel Icon Royalty", price=999, category="Solar Panel light", stock_quantity=50, image_url="https://atlas-content-cdn.pixelsquid.com/stock-images/solar-panel-cell-RB7AlaB-600.jpg", functionality="Portable"),
        Product(name="Solar Wall Lamp", price=699, category="Solar Wall Light", stock_quantity=100, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGJiX1U-dGICpkL7ndl7BvnLBcotFVpo77OA&s", functionality="Wall-mounted light"),
        Product(name="Solar Street Light Outo Wall Light", price=199, category="Solar Steet Light", stock_quantity=200, image_url="https://ke.jumia.is/unsafe/fit-in/500x500/filters:fill(white)/product/87/7486412/1.jpg?3618", functionality="Street light"),
    ]

    orders = [
        Order(user_id=1, order_date=date(2024, 8, 1), total_price=1698),
        Order(user_id=2, order_date=date(2024, 8, 2), total_price=999),
    ]

    order_products = [
        OrderProduct(order_id=1, product_id=1, quantity=1),
        OrderProduct(order_id=1, product_id=2, quantity=1),
        OrderProduct(order_id=2, product_id=3, quantity=1),
    ]

    reviews = [
        Review(user_id=1, product_id=1, comments="The solar panel works great! It's very portable and easy to set up.", rating=5, review_date=date(2024, 8, 1)),
        Review(user_id=2, product_id=2, comments="The solar wall lamp provides excellent lighting and is easy to install.", rating=4, review_date=date(2024, 8, 2)),
        Review(user_id=1, product_id=3, comments="The street light is very bright and covers a wide area. Good value for the price.", rating=4, review_date=date(2024, 8, 3)),
    ]

    db.session.add_all(users)
    db.session.add_all(products)
    db.session.add_all(orders)
    db.session.add_all(order_products)
    db.session.add_all(reviews)

    db.session.commit()


print("Data Seeded Successfully")