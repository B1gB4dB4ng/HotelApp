from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(hashed_password, plain_password)
