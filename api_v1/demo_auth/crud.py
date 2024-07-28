from auth import utils as auth_utils
from users.schemas import UserSchema

John = UserSchema(
    username="John",
    password=auth_utils.hash_password("qwerty"),
    email="Jonh@example.com",
    active=True,
)
Samium = UserSchema(
    username="Samium",
    password=auth_utils.hash_password("secret"),
    active=True,
)
user_db: dict[str, UserSchema] = {
    John.username: John,
    Samium.username: Samium,
}
