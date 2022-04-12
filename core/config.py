import os

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

class Settings:
    PROJECT_NAME: str = "Book Exchange Club"
    PROJECT_VERSION: str = "1.0.0"

    USE_SQLITE_DB: str = "False"

    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    ACCESS_TOKEN_EXPIRE_MINUTES = 172800  # in mins

    TEST_USER_EMAIL = "test@example.com"

settings = Settings()
