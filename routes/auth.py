from fastapi import APIRouter, Depends
from scheme.models import User, UserAuth, Token
from passlib.hash import bcrypt
from fastapi.security import OAuth2PasswordRequestForm
from utils.jwt import create_access_token
from utils.sqlalchemy import SessionLocal
import uuid
import secrets

router = APIRouter(
    tags=["Auth"],
    prefix="/auth"
)

@router.post("/signup")
async def create_user(user: UserAuth):
    """
    # Маршрут для регистрации нового пользователя

    - **username**: Username of the user (string)
    - **password**: Password of the user (string)
    """
    # Создание сессии БД
    db = SessionLocal()
    # Проверка на совпадение имени пользователя с существующими
    check_username = db.query(User).filter(User.username == user.username).first()
    if check_username is not None:
        db.close()
        return {"detail":"Пользователь с таким именем уже существует"}
    
    # Хеширование пароля перед сохранением в БД
    password_hash = bcrypt.hash(user.password)
    # Создание новой записи пользователя
    db_user = User(username=user.username, password_hash=password_hash)
    # Добавление пользователя в сессию БД
    db.add(db_user)
    # Фиксация изменений в БД
    db.commit()
    # Закрытие сессии БД
    db.close()
    return {"detail": "Пользователь создан", "username": user.username} 

# Маршрут для проверки логина и пароля пользователя
@router.post("/signin")
async def login_user(user_auth: OAuth2PasswordRequestForm = Depends()):
    """
    # Маршрут для авторизации пользователя, 
    # и получения токена

    - **username**: Username of the user (string)
    - **password**: Password of the user (string)
    """
    # Создание сессии БД
    db = SessionLocal()
    try:
        # Проверка наличия пользователя с таким именем в БД
        db_user = db.query(User).filter(User.username == user_auth.username).first()
        if db_user is None:
            return {"detail": "Пользователь не найден"}
        if bcrypt.verify(user_auth.password, db_user.password_hash):
            # Генерация нового токена доступа
            access_token = create_access_token(user_auth.username)
            
            # Проверка наличия существующего токена для пользователя
            existing_token = db.query(Token).filter(Token.user_id == db_user.id).first()
            if existing_token:
                # Обновление существующий токен
                existing_token = access_token.decode()
                # Фиксация изменений в БД
                db.commit()
            else:
                # Создание новой записи токена
                token_secret = secrets.token_urlsafe(16)
                token_id = str(uuid.uuid4())
                db_token = Token(id=token_id,
                                 token=access_token.decode(),
                                 secret=token_secret,
                                 user_id=db_user.id)
                # Добавление токена в сессию БД
                db.add(db_token)
                # Фиксация изменений в БД
                db.commit()
            
            # Обновление экземпляра db_user, чтобы привязать его к сессии
            db.refresh(db_user)
            
            # Возвращаем логин, токен и статус успешной проверки логина и пароля
            return {"detail": "Успешный вход",
                    "username": user_auth.username,
                    "id": db_user.id,
                    "access_token": access_token,
                    "token_type": "bearer"}
        else:
            # В случае неудачной проверки логина и пароля возвращаем ошибку
            return {"detail": "Неверный пароль"} if db_user else {"detail": "Пользователь не найден"}
    finally:
        # Закрытие сессии БД
        db.close()