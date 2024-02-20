import random
import secrets

from flask import Flask, request, session
from flask_session import Session
from bcrypt import hashpw, gensalt, checkpw
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from config import DATABASE_URL, UserTypes, ALLOWED_FILE_EXTENSIONS, ALLOWED_ENDPOINTS_FOR_CLIENT, ALLOWED_ENDPOINTS_FOR_OPS, ALLOWED_ENDPOINTS_FOR_ALL


app = Flask(__name__, static_folder="uploads")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
Session(app)

db = SQLAlchemy(app)


OTP_DICT = {}


class User(db.Model):
    """
    User model
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    hashed_password = db.Column(db.String)
    user_type = db.Column(db.String)


class File(db.Model):
    """
    File model
    """
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String)
    file_hash = db.Column(db.String)


def _generate_otp_and_send_to_mail(email):
    """
    Generate OTP and send to user email
    """
    otp = random.randint(100000, 999999)
    # TODO: Send OTP to user email
    return otp


@app.before_request
def validate_user():
    """
    Validate user
    """
    request_path = request.path.split("?")[0]
    if request.path in ALLOWED_ENDPOINTS_FOR_ALL:
        return
    user_type = session.get("user_type")
    if not user_type:
        return {
            "status": False,
            "message": "Please login to access this endpoint"
        }, 401
    
    if user_type == UserTypes.CLIENT:
        if request_path not in ALLOWED_ENDPOINTS_FOR_CLIENT:
            return {
                "status": False,
                "message": "CLIENT is not allowed to perform this action"
            }, 401
        
    elif user_type == UserTypes.OPS:
        if request_path not in ALLOWED_ENDPOINTS_FOR_OPS:
            return {
                "status": False,
                "message": "OPERATIONAL USER is not allowed to perform this action"
            }, 401
        
    else:
        return {
            "status": False,
            "message": "Unauthorized"
        }, 401


@app.route("/")
def index():
    db.create_all()
    return "Hello, World!"


@app.route("/user/signup", methods=["POST"])
def signup():
    """
    User signup
    """
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    user_type = request.form.get("user_type")

    if not username or not email or not password or not user_type:
        return {
            "status": False,
            "message": "Missing required fields"
        }, 400
    
    if user_type not in ["CLIENT", "OPS"]:
        return {
            "status": False,
            "message": "Invalid user type"
        }, 400
    
    hashed_password = hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")
    try:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return {
            "status": True,
            "message": "User created successfully",
            "user_id": user.id,
        }, 201
    except IntegrityError:
        return {
            "status": False,
            "message": "User with this username or email already exists"
        }, 409


@app.route("/user/request-otp", methods=["POST"])
def request_otp():
    """
    Send OTP to user email
    """
    email = request.json.get("email")
    if not email:
        return {
            "status": False,
            "message": "Missing required fields"
        }, 400
    
    otp = _generate_otp_and_send_to_mail(email)
    OTP_DICT[email] = otp
    return {
        "status": True,
        "message": "OTP generated successfully",
        "OTP": otp
    }


@app.route("/user/verify-otp", methods=["POST"])
def verify_otp():
    """
    Verify OTP
    """
    email = request.json.get("email")
    otp = request.json.get("otp")
    if not email or not otp:
        return {
            "status": False,
            "message": "Missing required fields"
        }, 400
    
    if email not in OTP_DICT:
        return {
            "status": False,
            "message": "OTP not found"
        }, 404
    
    if OTP_DICT[email] != otp:
        return {
            "status": False,
            "message": "Invalid OTP"
        }, 400
    
    return {
        "status": True,
        "message": "Email verified successfully"
    }


@app.route("/user/login", methods=["POST", "GET"])
def login():
    """
    User login
    """
    username = request.form.get("username", request.args.get("username"))
    password = request.form.get("password", request.args.get("password"))
    if not username or not password:
        return {
            "status": False,
            "message": "Missing required fields"
        }, 400
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return {
            "status": False,
            "message": "User not found"
        }, 404
    
    if not checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        return {
            "status": False,
            "message": "Invalid credentials"
        }, 401
    
    session["user_id"] = user.id
    session["user_type"] = user.user_type
    return {
        "status": True,
        "message": "User logged in successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_type": user.user_type
        },
    }


@app.route("/user/logout", methods=["POST", "GET"])
def logout():
    """
    User logout
    """
    print(session.get("user_id"), session.get("user_type"))
    session.pop("user_id", None)
    session.pop("user_type", None)

    return {
        "status": True,
        "message": "User logged out successfully"
    }


@app.route("/file/upload", methods=["POST"])
def upload_file():
    """
    Upload file
    """
    file = request.files.get("file")
    if not file:
        return {
            "status": False,
            "message": "Missing required fields"
        }, 400
    
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        return {
            "status": False,
            "message": "Invalid file type"
        }, 400

    file_name = file.filename
    file_hash = secrets.token_hex(16)
    file.save(f"uploads/{file_hash}.{file_extension}")
    file = File(
        file_name=file_name,
        file_hash=file_hash
    )
    db.session.add(file)
    db.session.commit()
    db.session.refresh(file)
    return {
        "status": True,
        "message": "File uploaded successfully",
        "file_id": file.id,
    }, 201


@app.route("/file/list", methods=["GET"])
def list_files():
    """
    List files
    """
    files = File.query.all()
    return {
        "status": True,
        "files": [
            {
                "download_link": f"/file/download?file_hash={file.file_hash}",
            }
            for file in files
        ]
    }


@app.route("/file/download", methods=["GET"])
def download_file():
    """
    Download file
    """
    file_hash = request.args.get("file_hash")
    file = File.query.filter_by(file_hash=file_hash).first()
    if not file:
        return {
            "status": False,
            "message": "File not found"
        }, 404
    
    filename = file.file_name
    file_extension = filename.split(".")[-1].lower()
    
    return app.send_static_file(f"{file_hash}.{file_extension}")


if __name__ == "__main__":
    app.run(debug=True)