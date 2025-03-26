from fastapi import HTTPException, Request, status
from jose import jwt
from jose.exceptions import JWTError
from sqladmin.authentication import AuthenticationBackend

from core.settings import settings


class BasicAuthBackend(AuthenticationBackend):  # type: ignore
    def __init__(
        self,
        username: str = settings.USER_ADMIN,
        password: str = settings.PASS_ADMIN,
    ):
        super().__init__(settings.SECRET_KEY)
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
        token = jwt.encode(
            {"sub": username},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

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
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            return False
        username = payload.get("sub")
        return bool(username == self.username)  # Проверка роли
