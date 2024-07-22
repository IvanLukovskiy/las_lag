from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.mixins import UserRelationMixin


class Post(Base, UserRelationMixin):
    _user_back_populates = "posts"

    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )
