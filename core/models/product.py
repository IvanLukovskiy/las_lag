from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .order_product_ossociation import OrderProductAssociation


class Product(Base):
    name: Mapped[str]
    price: Mapped[int]
    description: Mapped[str]
    # orders: Mapped[list["Order"]] = relationship(
    #     secondary="order_product_association",
    #     back_populates="products",
    # )
    orders_details: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="product",
    )
