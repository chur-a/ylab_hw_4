from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.sql import text
from fastapi_jwt_auth import AuthJWT

from src.db.db import engine
from ..schemas.users import UserCreate, UserLogin, UserUpdate, Tokens
import src.services.user as service
import src.services.auth as auth


router = APIRouter()


@router.post('/signup', summary="Регистрируется на сайте", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    if not service.check_email_on_valid(user.email):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid email')
    service.check_email_password_used(user)
    service.user_creation(user)
    return "User is successfully created"


@router.post('/login', summary="Заходит на сайт", response_model=Tokens)
def login_user(user: UserLogin, Authorize: AuthJWT = Depends()):
    flag, acc_tok, ref_tok = service.check_on_refresh_tk(Authorize)
    if flag:
        return {"access_token": acc_tok, "refresh_token": ref_tok}
    stmt = text("SELECT userid, password FROM users WHERE username = :x OR email = :x")
    with engine.connect() as conn:
        result = conn.execute(stmt, {"x": user.username})
        result = result.fetchone()
    service.check_login_and_password(result, user)
    acc_tok, ref_tok = auth.access_t(result.userid, Authorize), auth.refresh_t(result.userid, Authorize)
    jti_a, jti_b = Authorize.get_jti(acc_tok), Authorize.get_jti(ref_tok)
    auth.delete_tokens()
    auth.insert_tokens(acc_tok, jti_a, ref_tok, jti_b)
    return {"access_token": acc_tok, "refresh_token": ref_tok}


@router.get('/users/me', summary="Смотрит свой профиль")
def get_me(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    current_user = Authorize.get_jwt_subject()
    stmt = text("SELECT username, email FROM users WHERE userid = :x")
    with engine.connect() as conn:
        result = conn.execute(stmt, {"x": current_user})
    return result.fetchall()


@router.patch('/users/me', summary="Обновляет информацию о себе")
def update_me(user: UserUpdate, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    current_user = Authorize.get_jwt_subject()
    stmt = text("UPDATE users "
                "SET username = COALESCE(:x, username), email = COALESCE(:y, email) "
                "WHERE userid = :z")
    with engine.connect() as conn:
        conn.execute(stmt, {"x": user.username, "y": user.email, "z": current_user})
        conn.commit()
    response_stmt = text("SELECT * "
                         "FROM users "
                         "WHERE userid = :x")
    with engine.connect() as conn:
        result = conn.execute(response_stmt, {"x": current_user})
    return {"message": "Updated", "user": result.fetchall(), "access_token": auth.get_a_token()}


@router.post("/refresh", summary="Обновляет токен", response_model=Tokens)
def refresh(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    new_jti_a = Authorize.get_jti(new_access_token)
    auth.revoke_token("access_token")
    auth.update_access_token(new_access_token, new_jti_a)
    return {"access_token": new_access_token, "refresh_token": auth.get_r_token()}


@router.post("/logout", summary="Выйти из аккаунта")
def logout():
    auth.revoke_token("access_token")
    return {"msg": "Logout"}


@router.post("/logout_all", summary="Выйти со всех устройств")
def logout_all():
    auth.revoke_token("access_token")
    auth.revoke_token("refresh_token")
    auth.delete_tokens()
    return {"msg": "Logout_all"}
