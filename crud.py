import asyncio

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from api_v1.products.schemas import ProductCreate
from core.models import Order, OrderProductAssociation, Post, Product, Profile, User, db_helper


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    print("user", user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    # result: Result = await session.execute(stmt)
    # user: User | None = result.scalar_one_or_none()
    user: User | None = await session.scalar(stmt)
    print("user", user)
    return user


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    print("profile", profile)
    return profile


async def show_users_with_profiles(session: AsyncSession) -> list[User]:
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    print("users", users)
    for user in users:
        print("user", user)
        print("profile", user.profile.first_name)
    return list(users)


async def create_posts(
    session: AsyncSession,
    user_id: int,
    *posts_titles: str,
) -> list[Post]:
    posts = [Post(title=post_title, user_id=user_id) for post_title in posts_titles]
    session.add_all(posts)
    await session.commit()
    print("posts", posts)
    return posts


async def get_users_with_posts(
    session: AsyncSession,
) -> None:
    stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    # users = await session.scalars(stmt)
    result = await session.execute(stmt)
    users = result.scalars().unique()

    for user in users:
        print("**" * 10)
        print(user)
        for post in user.posts:
            print("-", post)


async def get_posts_with_authors(
    session: AsyncSession,
) -> None:
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    result = await session.execute(stmt)
    posts = result.scalars().unique()

    for post in posts:
        print("**" * 10)
        print(post)
        print(post.user)


async def get_users_with_posts_and_profiles(
    session: AsyncSession,
):
    stmt = (
        select(User)
        .options(
            joinedload(User.profile),
            selectinload(User.posts),
        )
        .order_by(User.id)
    )
    result = await session.execute(stmt)
    users = result.scalars().unique()

    for user in users:
        print("**" * 10)
        print(user, user.profile.first_name)
        for post in user.posts:
            print("-", post)


async def get_profiles_with_users_and_users_with_posts(session: AsyncSession) -> None:
    stmt = (
        select(Profile)
        .join(Profile.user)
        .options(
            joinedload(Profile.user).selectinload(User.posts),
        )
        .where(User.username == "John")
        .order_by(Profile.id)
    )
    result = await session.execute(stmt)
    profiles = result.scalars().unique()

    for profile in profiles:
        print("**" * 10)
        print(profile.first_name, profile.user)
        print(profile.user.posts)


async def create_order(
    session: AsyncSession,
    promocode: str | None = None,
) -> Order:
    order = Order(promocode=promocode)
    session.add(order)
    await session.commit()
    return order


async def create_product(
    session: AsyncSession,
    product_in: ProductCreate,
) -> Product:
    product = Product(**product_in.model_dump())
    session.add(product)
    await session.commit()
    return product


async def create_orders_and_products(session: AsyncSession):
    order_one = await create_order(session)
    order_promo = await create_order(session, promocode="promo")

    mouse = await create_product(
        session,
        ProductCreate(
            name="Mouse",
            price=100,
            description="Pro gaming Mouse",
        ),
    )
    keyboard = await create_product(
        session, ProductCreate(name="Keyboard", price=200, description="Pro gaming Keyboard,")
    )
    monitor = await create_product(
        session,
        ProductCreate(
            name="Monitor",
            price=300,
            description="Pro gaming Monitor",
        ),
    )

    order_one = await session.scalar(
        select(Order)
        .where(Order.id == order_one.id)
        .options(
            # selectinload(Order.products),
            selectinload(Order.products_details),
        ),
    )
    order_promo = await session.scalar(
        select(Order)
        .where(Order.id == order_promo.id)
        .options(
            # selectinload(Order.products),
            selectinload(Order.products_details),
        ),
    )

    order_one.products.append(mouse)
    order_one.products.append(keyboard)
    # order_promo.products.append(monitor)
    # order_promo.products.append(keyboard)
    order_promo.products = [monitor, keyboard]

    await session.commit()


# async def get_orders_with_products(
#     session: AsyncSession,
# ) -> list[Order]:
#     stmt = (
#         select(Order)
#         .options(
#             # selectinload(Order.products),
#             selectinload(Order.products_details),
#         )
#         .order_by(Order.id)
#     )
#     orders = await session.scalars(stmt)
#     return list(orders)


async def get_orders_with_products_assoc(
    session: AsyncSession,
) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products_details).joinedload(OrderProductAssociation.product),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)
    return list(orders)


# async def demo_get_orders_with_products_through_secondary(session: AsyncSession):
#     orders = await get_orders_with_products(session)
#     for order in orders:
#         print(order.id, order.promocode, order.created_at, "products:")
#         # for product in order.products:
#         for product in order.products_details:
#             print("-", product.id, product.name, product.price)


async def demo_get_orders_with_products_with_assoc(session: AsyncSession) -> list[Order]:
    orders = await get_orders_with_products_assoc(session)

    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")
        for order_product_details in order.products_details:
            print(
                "-",
                order_product_details.product.id,
                order_product_details.product.name,
                order_product_details.product.price,
                "qty:",
                order_product_details.count,
            )


async def create_gift_product_for_existing_orders(session: AsyncSession):
    orders = await get_orders_with_products_assoc(session)
    gift_product = await create_product(
        session,
        ProductCreate(
            name="Gift",
            price=0,
            description="Gift for you",
        ),
    )
    for order in orders:
        order.products_details.append(
            OrderProductAssociation(
                product=gift_product,
                count=1,
                unit_price=0,
            ),
        )
    await session.commit()


async def main_relations(session: AsyncSession):
    # await create_user(session, "John")
    # await create_user(session, "Jane")
    user_john = await get_user_by_username(session, "John")
    user_jane = await get_user_by_username(session, "Jane")
    # await create_user_profile(
    #     session,
    #     user_john.id,
    #     "John",
    # )
    # await create_user_profile(
    #     session,
    #     user_jane.id,
    #     "Jane",
    # )
    # await show_users_with_profiles(session)
    # await create_posts(
    #     session,
    #     user_john.id,
    #     "Hello",
    #     "World",
    #     "Foo",
    #     "Bar",
    # )
    # await create_posts(
    #     session,
    #     user_jane.id,
    #     "Hello2",
    #     "World2",
    #     "Foo2",
    #     "Bar2",
    # )
    # await get_users_with_posts(session)
    # await get_posts_with_authors(session)
    # await get_users_with_posts_and_profiles(session)
    # await get_profiles_with_users_and_users_with_posts(session)


async def demo_m2m(session: AsyncSession):
    # await create_orders_and_products(session)
    # await demo_get_orders_with_products_through_secondary(session)
    await demo_get_orders_with_products_with_assoc(session)
    # await create_gift_product_for_existing_orders(session)


async def main():
    async with db_helper.session_factory() as session:
        # await main_relations(session)
        await demo_m2m(session)


if __name__ == "__main__":
    asyncio.run(main())
