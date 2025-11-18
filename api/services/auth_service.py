from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

from api.database.connection import SessionLocal
from api.models.user import User

SECRET_KEY = "SECRET_TEMPORARIO"  # depois vamos ajustar isso
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str):
        return pwd_context.verify(password, hashed)

    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def register_user(user_data):
        db = SessionLocal()

        # verifica se usuário existe
        if db.query(User).filter(User.username == user_data.username).first():
            db.close()
            raise Exception("Username já existe")

        if db.query(User).filter(User.email == user_data.email).first():
            db.close()
            raise Exception("Email já existe")

        hashed = AuthService.hash_password(user_data.password)

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.close()

        return new_user

    @staticmethod
    def authenticate_user(username: str, password: str):
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.password):
            return None

        return user
 