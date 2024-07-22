from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.products import crud
from core.models import Product, db_helper


async def get_product_by_id(
    product_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.get_scoped_session),
) -> Product:
    product = await crud.get_product(session=session, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )
    return product
