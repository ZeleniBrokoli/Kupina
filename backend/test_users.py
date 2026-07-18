from models.user_model import create_user, find_user_by_email


create_user(
    "TestUser",
    "test@gmail.com",
    "12345"
)


user = find_user_by_email(
    "test@gmail.com"
)


print(user)