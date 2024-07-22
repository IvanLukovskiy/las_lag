from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.mixins import UserRelationMixin

if TYPE_CHECKING:
    pass


class Profile(Base, UserRelationMixin):
    _user_id_unique = True
    _user_back_populates = "profile"

    first_name: Mapped[str | None] = mapped_column(String(40))
    last_name: Mapped[str | None] = mapped_column(String(40))
    bio: Mapped[str | None] = mapped_column(Text, default="", server_default="")
