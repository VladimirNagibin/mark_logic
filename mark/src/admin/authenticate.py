from fastapi import HTTPException, Request, status
from jose import jwt
from jose.exceptions import JWTError
from sqladmin.authentication import AuthenticationBackend

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


class BasicAuthBackend(AuthenticationBackend):  # type: ignore
    def __init__(self, username: str, password: str):
        super().__init__(SECRET_KEY)
        self.username = username
        self.password = password

    async def login(self, request: Request) -> bool:
        """
        Проверка учетных данных пользователя.
        """
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if username != self.username or password != self.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

        # Генерация JWT токена
        token = jwt.encode({"sub": username}, SECRET_KEY, algorithm=ALGORITHM)

        # Сохранение токена в сессии
        request.session.update({"token": token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            return bool(username == self.username)  # Проверка роли
        except JWTError:
            return False
