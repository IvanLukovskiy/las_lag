import asyncio

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.models import Post, Profile, User, db_helper


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
):
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
):
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


async def get_profiles_with_users_and_users_with_posts(session: AsyncSession):
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


async def main():
    async with db_helper.session_factory() as session:
        # await create_user(session, "John")
        # await create_user(session, "Jane")
        # user_john = await get_user_by_username(session, "John")
        # user_jane = await get_user_by_username(session, "Jane")
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
        await get_profiles_with_users_and_users_with_posts(session)


if __name__ == "__main__":
    asyncio.run(main())
