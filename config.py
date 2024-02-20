from enum import Enum

class UserTypes:
    CLIENT = "CLIENT"
    OPS = "OPS"

ALLOWED_FILE_EXTENSIONS = ["pptx", "docx", "xlsx"]

ALLOWED_ENDPOINTS_FOR_CLIENT = [
    "/",
    "/user/signup",
    "/user/login",
    "/user/verify-otp",
    "/user/request-otp",
    "/file/download",
    "/file/list"
]

ALLOWED_ENDPOINTS_FOR_OPS = [
    "/",
    "/user/login",
    "/file/upload"
]

ALLOWED_ENDPOINTS_FOR_ALL = [
    "/",
    "/user/login",
    "/user/logout"
]

DATABASE_URL = "sqlite:///./db.sqlite3"