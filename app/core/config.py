import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-env")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
