from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.products import crud
from api_v1.products.dependencies import get_product_by_id
from api_v1.products.schemas import Product, ProductCreate, ProductUpdate, ProductUpdatePartial
from core.models import db_helper

router = APIRouter(tags=["Products"])


@router.get("/", response_model=list[Product])
async def get_products(session: AsyncSession = Depends(db_helper.get_scoped_session)) -> list[Product]:
    return await crud.get_products(session=session)


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_in: ProductCreate,
    session: AsyncSession = Depends(db_helper.get_scoped_session),
) -> Product:
    return await crud.create_product(session=session, product_in=product_in)


@router.get("/{product_id}/", response_model=Product)
async def get_product(
    product: Product = Depends(get_product_by_id),
) -> Product:
    return product


# @router.get("/{product_id}/", response_model=Product)
# async def get_product(
#     product_id: int,
#     session: AsyncSession = Depends(db_helper.get_scoped_session),
# ):
#     if product := await crud.get_product(session=session, product_id=product_id):
#         return product
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Product {product_id} not found",
#         )


@router.put("/{product_id}/", response_model=Product)
async def update_product(
    product_update: ProductUpdate,
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_helper.get_scoped_session),
) -> Product:
    return await crud.update_product(
        session=session,
        product=product,
        product_update=product_update,
    )


@router.patch("/{product_id}/", response_model=Product)
async def update_product_partial(
    product_update: ProductUpdatePartial,
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_helper.get_scoped_session),
) -> Product:
    return await crud.update_product(
        session=session,
        product=product,
        product_update=product_update,
        partial=True,
    )


@router.delete("/{product_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product: Product = Depends(get_product_by_id),
    session: AsyncSession = Depends(db_helper.get_scoped_session),
) -> None:
    await crud.delete_product(session=session, product=product)
