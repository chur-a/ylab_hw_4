from datetime import datetime

from ..db.db import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    views = Column(Integer, server_default='0')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.userid"))

    owners = relationship('User', back_populates="posts")


class User(Base):
    __tablename__ = 'users'

    userid = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    is_superuser = Column(Boolean, server_default='f')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("post", back_populates='owners')


class DenyTokens(Base):
    __tablename__ = "denylist"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String)


class CurrentTokens(Base):
    __tablename__ = 'validtokens'

    access_token = Column(String, primary_key=True)
    jti_a = Column(String)
    refresh_token = Column(String)
    jti_r = Column(String)
