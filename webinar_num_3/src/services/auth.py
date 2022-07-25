from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy.sql import text

from src.db.db import engine


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}


@AuthJWT.load_config
def get_config():
    return Settings()


@AuthJWT.token_in_denylist_loader
def check_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    stmt = text("SELECT * FROM denylist WHERE jti = :x")
    with engine.connect() as conn:
        result = conn.execute(stmt, {"x": jti})
    if result.fetchall():
        return True
    return False


def access_t(username: str, Authorize: AuthJWT = Depends()):
    access_token = Authorize.create_access_token(subject=username)
    return access_token


def refresh_t(username: str, Authorize: AuthJWT = Depends()):
    refresh_token = Authorize.create_refresh_token(subject=username)
    return refresh_token


def insert_tokens(access: str, jti_a: str, refresh: str, jti_r: str):
    stmt = text("INSERT INTO validtokens VALUES (:x, :y, :t, :z)")
    with engine.connect() as conn:
        conn.execute(stmt, {"x": access, "y": jti_a, "t": refresh, "z": jti_r})
        conn.commit()


def revoke_token(rv_token: str):
    if rv_token == "access_token":
        get_stmt = text("SELECT jti_a FROM validtokens")
    else:
        get_stmt = text("SELECT jti_r FROM validtokens")
    with engine.connect() as conn:
        result = conn.execute(get_stmt)
    jti = result.fetchone()[0]
    stmt = text("INSERT INTO denylist (jti) VALUES (:x)")
    with engine.connect() as conn:
        conn.execute(stmt, {"x": jti})
        conn.commit()


def update_access_token(token: str, jti: str):
    stmt = text("UPDATE validtokens SET access_token = :x, jti_a = :y")
    with engine.connect() as conn:
        conn.execute(stmt, {"x": token, "y": jti})
        conn.commit()


def get_a_token():
    get_stmt = text("SELECT access_token FROM validtokens")
    with engine.connect() as conn:
        result = conn.execute(get_stmt)
    return result.fetchone().access_token


def get_r_token():
    get_stmt = text("SELECT refresh_token FROM validtokens")
    with engine.connect() as conn:
        result = conn.execute(get_stmt)
    r_token = result.fetchone()
    if r_token:
        return r_token.refresh_token
    return


def delete_tokens():
    stmt = text("DELETE FROM validtokens")
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
