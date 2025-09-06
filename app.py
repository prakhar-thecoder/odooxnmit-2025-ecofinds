from datetime import *
from flask import *
import db_utils
import config
from werkzeug.security import *
from werkzeug.utils import *
from auth_utils import *
from functools import wraps

app = Flask(__name__)
app.config.from_object(config)

# Profile pics
PROFILE_UPLOAD_FOLDER = "static/uploads/profile_pics"
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)

# Product images
PRODUCT_UPLOAD_FOLDER = "static/uploads/products"
os.makedirs(PRODUCT_UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


@app.before_request
def load_logged_in_user():
    request.user = None
    token = request.cookies.get("auth_token")
    if token:
        rows = db_utils.select_query(
            """
            SELECT u.user_id, u.name, u.username, u.email, u.profile_pic
            FROM auths a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.token=%s AND (a.expires_at IS NULL OR a.expires_at > NOW())
            """,
            (token,),
        )
        if rows:
            request.user = rows[0]

@app.context_processor
def inject_user():
    return dict(current_user=request.user)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------- HOME --------------------
@app.route('/')
def index():
    # Only fetch fields needed for product listing
    query = """
        SELECT product_id, title, price, product_image, category 
        FROM products
    """
    products = db_utils.select_query(query)
    return render_template("index.html", products=products)

# -------------------- PRODUCT DETAIL --------------------
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    query = """
        SELECT product_id, user_id, title, description, category, price, product_image
        FROM products
        WHERE product_id = %s
    """
    product = db_utils.select_query(query, (product_id,))
    if not product:
        return "Product not found", 404
    return render_template("product_details.html", product=product[0])

@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    if request.method == "POST":
        name = request.form.get("display_name")  # treating display_name as name
        username = request.form.get("username") or name.lower().replace(" ", "")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            errors.append("Passwords do not match")
        else:
            existing = db_utils.select_query(
                "SELECT user_id FROM users WHERE email=%s OR username=%s",
                (email, username),
            )
            if existing:
                errors.append("Email or username already exists")
            else:
                password_hash = generate_password_hash(password)
                db_utils.insert_query(
                    """
                    INSERT INTO users (name, username, email, password_hash)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (name, username, email, password_hash),
                )
                return redirect("/login")

    return render_template("register.html", errors=errors)

@app.route("/login", methods=["GET", "POST"])
def login():
    errors = []
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db_utils.select_query(
            "SELECT user_id, password_hash FROM users WHERE email=%s", (email,)
        )

        if not user or not check_password_hash(user[0]["password_hash"], password):
            errors.append("Invalid email or password")
            return render_template("login.html", errors=errors)

        user_id = user[0]["user_id"]

        # generate token
        token = secrets.token_hex(32)
        db_utils.insert_query(
            "INSERT INTO auths (user_id, token) VALUES (%s, %s)",
            (user_id, token),
        )

        resp = redirect("/profile")
        resp.set_cookie("auth_token", token, httponly=True, samesite="Lax")
        return resp

    return render_template("login.html", errors=errors)

@app.route("/logout")
@require_auth
def logout():
    resp = redirect("/login")
    resp.delete_cookie("auth_token")
    return resp

@app.route("/profile", methods=["GET", "POST"])
@require_auth
def profile():
    user_id = request.user_id
    errors = []
    success = None

    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        contact_no = request.form.get("contact_no")

        # check duplicate username
        existing = db_utils.select_query(
            "SELECT user_id FROM users WHERE username=%s AND user_id!=%s",
            (username, user_id),
        )
        if existing:
            errors.append("Username already taken")
        else:
            profile_pic = None
            file = request.files.get("profile_pic")
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"user_{user_id}.{ext}"
                filepath = os.path.join(PROFILE_UPLOAD_FOLDER, filename)
                file.save(filepath)
                profile_pic = f"/static/uploads/profile_pics/{filename}"

            query = "UPDATE users SET name=%s, username=%s, contact_no=%s"
            params = [name, username, contact_no]

            if profile_pic:
                query += ", profile_pic=%s"
                params.append(profile_pic)

            query += " WHERE user_id=%s"
            params.append(user_id)

            db_utils.update_query(query, tuple(params))
            success = "Profile updated successfully"

    user = db_utils.select_query(
        "SELECT user_id, name, email, username, contact_no, profile_pic, created_at FROM users WHERE user_id=%s",
        (user_id,),
    )
    if not user:
        return "User not found", 404

    return render_template("profile.html", user=user[0], errors=errors, success=success)

# -------------------- ADD PRODUCT --------------------
@app.route("/products/add", methods=["GET", "POST"])
@require_auth
def add_product():
    errors, success = [], None
    user_id = request.user_id

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        price = request.form.get("price")

        if not title or not price or not category:
            errors.append("All required fields must be filled")
        else:
            db_utils.insert_query(
                """
                INSERT INTO products (user_id, title, description, category, price)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, title, description, category, price),
            )

            product = db_utils.select_query(
                "SELECT product_id FROM products WHERE user_id=%s ORDER BY product_id DESC LIMIT 1",
                (user_id,),
            )
            product_id = product[0]["product_id"]

            file = request.files.get("image")
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"product_{product_id}.{ext}"
                filepath = os.path.join(PRODUCT_UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_path = f"/uploads/products/{filename}"

                db_utils.update_query(
                    "UPDATE products SET product_image=%s WHERE product_id=%s",
                    (image_path, product_id),
                )

            return redirect("/my-products")

    return render_template("add_product.html", errors=errors, success=success)

@app.route("/my-products")
@require_auth
def my_products():
    user_id = request.user_id
    products = db_utils.select_query(
        "SELECT * FROM products WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    return render_template("my_products.html", products=products)

# -------------------- EDIT PRODUCT --------------------
@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@require_auth
def edit_product(product_id):
    user_id = request.user_id
    product = db_utils.select_query(
        "SELECT * FROM products WHERE product_id=%s AND user_id=%s",
        (product_id, user_id),
    )

    if not product:
        return "Product not found or unauthorized", 404

    product = product[0]
    errors, success = [], None

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")

        if not title or not price or not description:
            errors.append("All required fields must be filled")
        else:
            db_utils.update_query(
                """
                UPDATE products 
                SET title=%s, description=%s, price=%s, category=%s
                WHERE product_id=%s AND user_id=%s
                """,
                (title, description, price, product['category'], product_id, user_id),
            )

            success = "Product updated successfully"
            product = db_utils.select_query(
                "SELECT * FROM products WHERE product_id=%s AND user_id=%s",
                (product_id, user_id),
            )[0]

    return render_template("edit_product.html", product=product, errors=errors, success=success)

# -------------------- DELETE PRODUCT --------------------
@app.route("/products/delete/<int:product_id>", methods=["POST"])
@require_auth
def delete_product(product_id):
    user_id = request.user_id
    product = db_utils.select_query(
        "SELECT * FROM products WHERE product_id=%s AND user_id=%s",
        (product_id, user_id),
    )

    if not product:
        return "Product not found or unauthorized", 404

    db_utils.delete_query(
        "DELETE FROM products WHERE product_id=%s AND user_id=%s",
        (product_id, user_id),
    )

    return redirect("/my-products")


@app.route("/cart/add/<int:product_id>")
@require_auth
def add_to_cart(product_id):
    user_id = request.user_id

    # Fetch product price
    product = db_utils.select_query(
        "SELECT price FROM products WHERE product_id=%s", (product_id,)
    )
    if not product:
        return "Product not found", 404

    price = product[0]["price"]

    # insert fresh row
    db_utils.insert_query(
        "INSERT INTO cart (user_id, product_id, total_price) VALUES (%s, %s, %s)",
        (user_id, product_id, price),
    )

    return redirect("/cart")

# -------------------- VIEW CART --------------------
@app.route("/cart")
@require_auth
def view_cart():
    user_id = request.user_id
    items = db_utils.select_query(
        """
        SELECT c.cart_id, c.total_price, p.title, p.product_image, p.price
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id=%s
        ORDER BY c.added_at DESC
        """,
        (user_id,),
    )

    grand_total = sum(item["total_price"] for item in items) if items else 0

    return render_template("cart.html", items=items, grand_total=grand_total)

# -------------------- REMOVE ITEM FROM CART --------------------
@app.route("/cart/remove/<int:cart_id>", methods=["POST"])
@require_auth
def remove_from_cart(cart_id):
    user_id = request.user_id

    # Ensure item belongs to current user
    item = db_utils.select_query(
        "SELECT cart_id FROM cart WHERE cart_id=%s AND user_id=%s",
        (cart_id, user_id),
    )

    if not item:
        return "Item not found or unauthorized", 404

    db_utils.delete_query("DELETE FROM cart WHERE cart_id=%s AND user_id=%s", (cart_id, user_id))
    return redirect("/cart")

# -------------------- CHECKOUT --------------------
@app.route("/checkout", methods=["POST"])
@require_auth
def checkout():
    user_id = request.user_id

    cart_items = db_utils.select_query(
        "SELECT product_id, total_price FROM cart WHERE user_id=%s",
        (user_id,),
    )

    if not cart_items:
        return redirect("/cart")

    # Insert into purchase history
    for item in cart_items:
        db_utils.insert_query(
            """
            INSERT INTO product_purchase_history (user_id, product_id, total_price)
            VALUES (%s, %s, %s)
            """,
            (user_id, item["product_id"], item["total_price"]),
        )

    # Clear cart
    db_utils.delete_query("DELETE FROM cart WHERE user_id=%s", (user_id,))

    return render_template("checkout_success.html")

@app.route("/purchases")
@require_auth
def view_purchases():
    user_id = request.user_id
    purchases = db_utils.select_query(
        """
        SELECT ph.purchase_id, ph.total_price, ph.purchased_at,
               p.title, p.product_image
        FROM product_purchase_history ph
        JOIN products p ON ph.product_id = p.product_id
        WHERE ph.user_id=%s
        ORDER BY ph.purchased_at DESC
        """,
        (user_id,),
    )
    return render_template("purchases.html", purchases=purchases)


if __name__ == '__main__':
    app.run(debug=True)