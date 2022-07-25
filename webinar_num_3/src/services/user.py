import re
from datetime import datetime

from fastapi import HTTPException, status, Depends
from sqlalchemy.sql import text
import bcrypt
from fastapi_jwt_auth import AuthJWT

import src.services.auth as auth
from src.db.db import engine


def check_email_on_valid(email: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return False
    return True


def hash_password(password: str):
    byte_password = password.encode('utf-8')
    my_salt = bcrypt.gensalt()
    h_password = bcrypt.hashpw(byte_password, my_salt)
    return h_password.decode("utf-8")


def check_email_password_used(user):
    with engine.connect() as conn:
        stmt = text("SELECT username, email FROM users WHERE users.email = :x OR users.username = :y")
        result = conn.execute(stmt, {'x': user.email, 'y': user.username})
    for raw in result:
        if user.username in raw:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='This username is already used')
        if user.email in raw:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Email is already used')


def user_creation(user):
    stmt = text("INSERT INTO users (username, email, password) "
                "VALUES (:username, :email, :password)")
    user.password = hash_password(user.password)
    with engine.connect() as conn:
        conn.execute(stmt, dict(user))
        conn.commit()


def check_on_refresh_tk(Authorize: AuthJWT = Depends()):
    ref_tok = auth.get_r_token()
    if ref_tok:
        raw_ref_tok = Authorize.get_raw_jwt(ref_tok)
        now = datetime.now()
        now_timestamp = datetime.timestamp(now)
        if raw_ref_tok["exp"] >= now_timestamp:
            acc_tok = Authorize.create_access_token(subject=raw_ref_tok["sub"])
            new_jti_a = Authorize.get_jti(acc_tok)
            auth.update_access_token(acc_tok, new_jti_a)
            return True, acc_tok, ref_tok
    return False, None, None


def check_login_and_password(result, user):
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or email")
    password_h = result.password
    if not bcrypt.checkpw(user.password.encode("utf-8"), password_h.encode("utf-8")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
