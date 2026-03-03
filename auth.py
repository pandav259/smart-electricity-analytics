import bcrypt
from database import get_connection

# -----------------------
# Hash Password
# -----------------------
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

# -----------------------
# Verify Password
# -----------------------
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

# -----------------------
# Register User
# -----------------------
def register_user(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )

        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# -----------------------
# Login User
# -----------------------
def login_user(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, stored_hash = user
        if verify_password(password, stored_hash):
            return user_id

    return None