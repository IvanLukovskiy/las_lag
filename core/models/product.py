from sqlalchemy.orm import Mapped

from core.models.base import Base


class Product(Base):
    name: Mapped[str]
    price: Mapped[int]
    description: Mapped[str]
