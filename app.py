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
            SELECT u.user_id, u.name, u.username, u.email
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

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route("/products/add", methods=["GET", "POST"])
@require_auth
def add_product():
    errors = []
    success = None
    user_id = request.user_id

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        price = request.form.get("price")
        quantity = request.form.get("quantity", 1)
        item_condition = request.form.get("item_condition")

        if not title or not price or not category or not item_condition:
            errors.append("All required fields must be filled")
        else:
            # Insert product without image first to get product_id
            db_utils.insert_query(
                """
                INSERT INTO products (user_id, title, description, category, price, quantity, item_condition)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, title, description, category, price, quantity, item_condition)
            )

            # Get last inserted product_id
            product = db_utils.select_query(
                "SELECT product_id FROM products WHERE user_id=%s ORDER BY product_id DESC LIMIT 1",
                (user_id,)
            )
            product_id = product[0]["product_id"]

            # Handle file upload
            file = request.files.get("image")
            image_path = None
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"product_{product_id}.{ext}"
                filepath = os.path.join(PRODUCT_UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_path = f"/static/uploads/products/{filename}"

                # Update product record with image_path
                db_utils.update_query(
                    "UPDATE products SET product_image=%s WHERE product_id=%s",
                    (image_path, product_id)
                )

            success = "Product added successfully"

    return render_template("add_product.html", errors=errors, success=success)



if __name__ == '__main__':
    app.run(debug=True)
