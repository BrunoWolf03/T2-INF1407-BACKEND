from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt

from api.schemas.user_schema import UserCreate, UserLogin, UserPublic
from api.services.auth_service import AuthService, SECRET_KEY, ALGORITHM

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserPublic)
def register(user: UserCreate):
    new_user = AuthService.register_user(user)
    return new_user


@router.post("/login")
def login(credentials: UserLogin):
    user = AuthService.authenticate_user(credentials.username, credentials.password)

    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    token = AuthService.create_access_token({"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserPublic)
def me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token inválido")

    from api.database.connection import SessionLocal
    db = SessionLocal()

    user = db.query(User).filter_by(username=username).first()
    db.close()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user
