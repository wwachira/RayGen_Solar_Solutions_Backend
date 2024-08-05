from app import app, db;
from models import User, Product, Order, OrderProduct, Review;
from datetime import date;

with app.app_context():
   
    print("Deleting data...")
    OrderProduct.query.delete()
    Order.query.delete()
    Product.query.delete()
    User.query.delete()
    Review.query.delete()
      
      
    print("Creating users...")
    users = [
        User(name="Alice Smith", email="alice@example.com", password="password123", role="customer", phone_number="1234567890"),
        User(name="Bob Johnson", email="bob@example.com", password="password123", role="admin", phone_number="0987654321"),
        User(name="Charlie Brown", email="charlie@example.com", password="password123", role="customer",phone_number="0987654321"),
    ]
      
    print("Creating products...")
    products = [
        # Cartegory: Solar Panel Light
        Product(name="RadiantBeam Titan", price=999, category="Solar Panel light", stock_quantity=50, image_url="https://atlas-content-cdn.pixelsquid.com/stock-images/solar-panel-cell-RB7AlaB-600.jpg", functionality="Portable design with high efficiency"),
        Product(name="EcoRay Elite", price=1099, category="Solar Panel light", stock_quantity=40, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQTvsgp5ygto1x9lm52k8R-1mRz4BTA0_eZrgZE6xqGFpBV8zwt9Dl3m7duWmal5VE52xk&usqp=CAU", functionality="Advanced energy storage"),
        Product(name="RadiantLite MiniPro", price=499, category="Solar Panel light", stock_quantity=70, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZ2XNhi0N3UmOln9akTA6BJnR_hp_wqdpxSFTOMokR6B-b1Xd43G0cGlEdfpY4mzIiQ7A&usqp=CAU", functionality="Compact and lightweight"),
        Product(name="EcoGlow Aura", price=899, category="Solar Panel light", stock_quantity=60, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRk80ef5WN1HhIMXKRLtwxrJJD4Fauhl56nT4oNWrJiaWtZLuAaq2NuxbUEhoVxjxvhpbU&usqp=CAU", functionality="Environmentally friendly"),
        Product(name="RadiantTech Quantum", price=1299, category="Solar Panel light", stock_quantity=30, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRkeZts7rjaYuyjiY8bNGxeWB-lopTlLkCz2rlKYmr7jWSIqp16UrE6enRwuDRnMFR7QoI&usqp=CAU", functionality="Cutting-edge technology"),
        Product(name="EcoRay Basic", price=399, category="Solar Panel light", stock_quantity=80, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQes-Gr5_Ar6kqX9e0WcEesCvCS1O9tUrC6WlwCTWMhi-DeCI0uM22DdxzH8QlCkAjfsn0&usqp=CAU", functionality="Affordable and reliable"),
        Product(name="RadiantBeam Supreme", price=1399, category="Solar Panel light", stock_quantity=25, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT0P3PT6zaF5u2gN5S8SYgmtUT7RYlSYsXFx26i8wME0JweU4jJ6_itouqZvZueKQji1cw&usqp=CAU", functionality="High-end performance"),
        Product(name="EcoGlow Standard", price=799, category="Solar Panel light", stock_quantity=65, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLgc-O39DjsMD99Vn4qw3r0PZ2jwCpx130qcZc9SNtShrHEFEzBXgKcF6fZzrhv5OCDLk&usqp=CAU", functionality="Standard model with good efficiency"),

        # Category: Solar Wall Light
        Product(name="RadiantGuard Sensor Lamp", price=699, category="Solar Wall Light", stock_quantity=100, image_url="https://m.media-amazon.com/images/I/71I3wrcGxVL._AC_UF1000,1000_QL80_.jpg",  functionality="Wall-mounted with motion sensor"),
        Product(name="RadiantPro LED Light", price=799, category="Solar Wall Light", stock_quantity=90, image_url="https://images-cdn.ubuy.co.in/634d2897e7c8f54afc62b756-solar-wall-lights-outdoor-solar-deck.jpg", functionality="High brightness with wide coverage"),
        Product(name="RadiantMini LED", price=299, category="Solar Wall Light", stock_quantity=150, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGJiX1U-dGICpkL7ndl7BvnLBcotFVpo77OA&s", functionality="Compact and bright for small areas"),
        Product(name="EcoRay LED Light", price=599, category="Solar Wall Light", stock_quantity=110, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpAjvVRiRmN1afrA5Jszo6sNIsQPi5c5g8uC7-JPXvHKWfJRDDhNqig0Krv5PFOOgtt0o&usqp=CAU", functionality="Energy efficient with long lifespan"),
        Product(name="RadiantAdvanced LED", price=999, category="Solar Wall Light", stock_quantity=70, image_url="https://ke.jumia.is/unsafe/fit-in/500x500/filters:fill(white)/product/14/2527251/1.jpg?7505", functionality="Advanced features and design"),
        Product(name="LumenBasic LED", price=199, category="Solar Wall Light", stock_quantity=200, image_url="https://solarshop.co.ke/wp-content/uploads/2024/03/ezgif.com-webp-to-jpg-1.jpg", functionality="Simple and affordable"),
        Product(name="LumenPremium Remote ", price=1099, category="Solar Wall Light", stock_quantity=60, image_url="https://www.thesolarcentre.co.uk/images/products/csudwlae.jpg", functionality="Premium build with remote control"),
        Product(name="LumenStandard LED", price=499, category="Solar Wall Light", stock_quantity=130, image_url="https://lw-cdn.com/images/BC213A20CDB9/k_80f12ed2e1ca2fd4a4ac782f4981730d;w_1600;h_1600;q_100/8614014.jpg", functionality="Standard model with good performance"),

        # Category: Solar Street Light
        Product(name="SolRay Outo Street Light", price=199, category="Solar Street Light", stock_quantity=200, image_url="https://ke.jumia.is/unsafe/fit-in/500x500/filters:fill(white)/product/87/7486412/1.jpg?3618", functionality="Street light with wide coverage"),
        Product(name="Radiant Pro Street Light", price=399, category="Solar Street Light", stock_quantity=180, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdMHxy6dTtWyq3VvmyJh6y8dyJNrhYFTwEirseUzxe35Ega39msXDZDXhEJHcxE323_GM&usqp=CAU", functionality="High intensity for large areas"),
        Product(name="", price=149, category="Solar Street Light", stock_quantity=220, image_url="https://ke.jumia.is/unsafe/fit-in/500x500/filters:fill(white)/product/92/9204151/1.jpg?1994", functionality="Compact design for narrow spaces"),
        Product(name="", price=299, category="Solar Street Light", stock_quantity=190, image_url="https://fireflier.com/wp-content/uploads/2021/05/remote-control-solar-street-lighting.jpg", functionality="Energy efficient with remote control"),
        Product(name="", price=499, category="Solar Street Light", stock_quantity=160, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTEQrwoU0vONgkGodxkgshE8eGSPr7UqIcyOGS5NIrUNaMANKfjCOtjzM9PefiyU-7eGUo&usqp=CAU", functionality="Advanced features and high durability"),
        Product(name="", price=99, category="Solar Street Light", stock_quantity=250, image_url="https://solarstore.co.ke/wp-content/uploads/2022/11/100-Watts-Neelux-Solar-Integrated-Solar-Street-Light.jpg", functionality="Basic and cost-effective"),
        Product(name="", price=599, category="Solar Street Light", stock_quantity=140, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbOUkLaANPNhTpwwp4XrpDWXxChHH1JTXY-7vnIYXlnD_suM1g-O12f94auxcSsWxwRBg&usqp=CAU", functionality="Premium features with smart control"),
        Product(name="", price=249, category="Solar Street Light", stock_quantity=210, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT8MDrQ3guqbOvmGYRHXw5AxG1X-keBnuT5JF_B9OF6ATYygku50dukD05HJLi_mIbAFds&usqp=CAU", functionality="Standard model with good efficiency"),
    ]
      
    print("Creating orders...")
    orders = [
        Order(user_id=1, order_date=date(2024, 8, 1), total_price=1698),
        Order(user_id=2, order_date=date(2024, 8, 2), total_price=999),
        Order(user_id=3, order_date=date(2024, 8, 3), total_price=1799),
    ]
    print("Creating orderproducts...") 
    order_products = [
        OrderProduct(order_id=1, product_id=1, quantity=1),
        OrderProduct(order_id=1, product_id=2, quantity=1),
        OrderProduct(order_id=2, product_id=3, quantity=3),
        OrderProduct(order_id=3, product_id=4, quantity=5),
        OrderProduct(order_id=3, product_id=5, quantity=2),
        OrderProduct(order_id=3, product_id=6, quantity=2),
        OrderProduct(order_id=3, product_id=7, quantity=2),
        OrderProduct(order_id=3, product_id=8, quantity=3),
        OrderProduct(order_id=3, product_id=9, quantity=3),
        OrderProduct(order_id=4, product_id=10, quantity=3),
        OrderProduct(order_id=2, product_id=11, quantity=6),
        OrderProduct(order_id=4, product_id=12, quantity=6),
        OrderProduct(order_id=2, product_id=13, quantity=6),
        OrderProduct(order_id=1, product_id=14, quantity=2),
        OrderProduct(order_id=5, product_id=15, quantity=1),
        OrderProduct(order_id=2, product_id=16, quantity=1),
        OrderProduct(order_id=2, product_id=17, quantity=3),
        OrderProduct(order_id=3, product_id=18, quantity=1),
        OrderProduct(order_id=1, product_id=19, quantity=1),
        OrderProduct(order_id=4, product_id=20, quantity=4),
        OrderProduct(order_id=1, product_id=21, quantity=4),
        OrderProduct(order_id=2, product_id=22, quantity=4),
        OrderProduct(order_id=3, product_id=23, quantity=1),
        OrderProduct(order_id=3, product_id=24, quantity=1),
    ]
    print("Creating reviews ...")
    reviews = [
        Review(user_id=1, product_id=1, comments="The solar panel works great! It's very portable and easy to set up.", rating=5, review_date=date(2024, 8, 1)),
        Review(user_id=2, product_id=2, comments="The solar wall lamp provides excellent lighting and is easy to install.", rating=4, review_date=date(2024, 8, 2)),
        Review(user_id=1, product_id=3, comments="The street light is very bright and covers a wide area. Good value for the price.", rating=4, review_date=date(2024, 8, 3)),
        Review(user_id=1, product_id=4, comments="The solar panel eco is environmentally friendly and efficient.", rating=5, review_date=date(2024, 8, 4)),
        Review(user_id=2, product_id=5, comments="The advanced solar panel has cutting-edge technology.", rating=4, review_date=date(2024, 8, 5)),
        Review(user_id=3, product_id=6, comments="The basic solar panel is affordable and reliable.", rating=4, review_date=date(2024, 8, 6)),
        Review(user_id=1, product_id=7, comments="The premium solar panel offers high-end performance.", rating=5, review_date=date(2024, 8, 7)),
        Review(user_id=2, product_id=8, comments="The standard solar panel has good efficiency.", rating=4, review_date=date(2024, 8, 8)),
        Review(user_id=3, product_id=9, comments="The solar wall lamp is wall-mounted with a motion sensor.", rating=5, review_date=date(2024, 8, 9)),
        Review(user_id=1, product_id=10, comments="The pro solar wall light has high brightness and wide coverage.", rating=4, review_date=date(2024, 8, 10)),
        Review(user_id=2, product_id=11, comments="The mini solar wall light is compact and bright.", rating=4, review_date=date(2024, 8, 11)),
        Review(user_id=3, product_id=12, comments="The eco solar wall light is energy efficient with a long lifespan.", rating=5, review_date=date(2024, 8, 12)),
        Review(user_id=1, product_id=13, comments="The advanced solar wall light has advanced features and design.", rating=4, review_date=date(2024, 8, 13)),
        Review(user_id=2, product_id=14, comments="The basic solar wall light is simple and affordable.", rating=4, review_date=date(2024, 8, 14)),
        Review(user_id=3, product_id=15, comments="The premium solar wall light has a premium build and remote control.", rating=5, review_date=date(2024, 8, 15)),
        Review(user_id=1, product_id=16, comments="The standard solar wall light has good performance.", rating=4, review_date=date(2024, 8, 16)),
        Review(user_id=2, product_id=17, comments="The solar street light has wide coverage.", rating=5, review_date=date(2024, 8, 17)),
        Review(user_id=3, product_id=18, comments="The pro solar street light has high intensity for large areas.", rating=4, review_date=date(2024, 8, 18)),
        Review(user_id=1, product_id=19, comments="The mini solar street light is compact for narrow spaces.", rating=4, review_date=date(2024, 8, 19)),
        Review(user_id=2, product_id=20, comments="The eco solar street light is energy efficient with remote control.", rating=5, review_date=date(2024, 8, 20)),
        Review(user_id=3, product_id=21, comments="The advanced solar street light has advanced features and high durability.", rating=4, review_date=date(2024, 8, 21)),
        Review(user_id=1, product_id=22, comments="The basic solar street light is cost-effective.", rating=4, review_date=date(2024, 8, 22)),
        Review(user_id=2, product_id=23, comments="The premium solar street light has smart control.", rating=5, review_date=date(2024, 8, 23)),
        Review(user_id=3, product_id=24, comments="The standard solar street light has good efficiency.", rating=4, review_date=date(2024, 8, 24)),
    ]

    db.session.add_all(users)
    db.session.add_all(products)
    db.session.add_all(orders)
    db.session.add_all(order_products)
    db.session.add_all(reviews)

    db.session.commit()


print("Data Seeded Successfully")