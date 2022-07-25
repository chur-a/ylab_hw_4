import json
from functools import lru_cache
from typing import Optional

from fastapi import Depends
from sqlmodel import Session
from sqlalchemy.sql import text

from src.api.v1.schemas import PostCreate
from src.db import AbstractCache, get_cache, get_session, engine
from src.models import Post
from src.services import ServiceMixin

__all__ = ("PostService", "get_post_service")


class PostService(ServiceMixin):
    def get_post_list(self) -> dict:
        """Получить список постов."""
        stmt = text("SELECT * FROM post")
        with engine.connect() as conn:
            result = conn.execute(stmt)
        return {"posts": [post for post in result]}

    def get_post_detail(self, item_id: int) -> Optional[dict]:
        """Получить детальную информацию поста."""
        if cached_post := self.cache.get(key=f"{item_id}"):
            return json.loads(cached_post)

        post = self.session.query(Post).filter(Post.id == item_id).first()
        if post:
            self.cache.set(key=f"{post.id}", value=post.json())
        return post.dict() if post else None

    def create_post(self, post: PostCreate, user_id: int) -> dict:
        """Создать пост."""
        stmt = text("INSERT INTO post (title, description, owner_id) "
                    "VALUES (:x, :y, :z)")
        with engine.connect() as conn:
            conn.execute(stmt, {"x": post.title, "y": post.description, "z": user_id})
            conn.commit()
        response_stmt = text("SELECT * FROM post WHERE title = :x AND description = :y")
        with engine.connect() as conn:
            result = conn.execute(response_stmt, {"x": post.title, "y": post.description})
        return result.fetchone()


# get_post_service — это провайдер PostService. Синглтон
@lru_cache()
def get_post_service(
    cache: AbstractCache = Depends(get_cache),
    session: Session = Depends(get_session),
) -> PostService:
    return PostService(cache=cache, session=session)
