from fastapi import APIRouter, Depends
from utils.jwt import validate_token
from utils.sqlalchemy import SessionLocal
from utils.errors import bad_request, unauthorized, forbidden, not_found
from fastapi.security import OAuth2PasswordBearer
from scheme.models import Message, Token, Like, Dislike

# Инициализация роутера
router = APIRouter(
    tags=["Messages"],
    prefix="/chat"
)
# Схема аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

@router.post('/messages/{message_id}/like')
async def like_message(message_id: str, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для создания лайка для сообщения  
    # (кроме своих) по message id
    """
    # Проверка валидности токена
    valid_token = validate_token(token)
    if not valid_token:
        unauthorized("Упс! Вам нужно авторизироваться")

    # Создание сессии БД
    db = SessionLocal()
    allow_token = db.query(Token).filter(Token.token == token).first()
    if not allow_token:
        db.close()
        unauthorized("Некорректный токен")

    # Получение идентификатора пользователя из токена
    user_id = allow_token.user_id

    # Проверка, что пользователь не является отправителем сообщения
    sender_id = (
        db.query(Message.sender_id)
        .filter(Message.id == message_id)
        .scalar()
    )
    if sender_id == user_id:
        db.close()
        forbidden("Вы не можете ставить лайк на своё сообщение")
    
    # Проверка, был ли уже установлен лайк для данного сообщения
    existing_like = (
        db.query(Like)
        .filter(Like.user_id == user_id, Like.message_id == message_id)
        .first()
    )
    if existing_like:
        db.close()
        bad_request("Лайк уже установлен")
    # Проверка, было ли сообщение удалено
    message = (
        db.query(Message)
        .filter(Message.id == message_id, Message.is_deleted == False)
        .first()
    )
    if not message:
        db.close()
        not_found("Сообщение не найдено")
    # Создание записи о лайке
    like = Like(user_id=user_id, message_id=message_id, is_like=True)
    db.add(like)
    db.commit()
    # Закрытие сессии БД
    db.close()
    # Возвращаем статус успешной установки лайка
    return {"detail": "Лайк установлен"}

@router.post('/messages/{message_id}/dislike')
async def dislike_message(message_id: str, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для создания дислайка для сообщения 
    # (кроме своих) по message id
    """
    # Проверка валидности токена
    valid_token = validate_token(token)
    if not valid_token:
        unauthorized("Упс! Вам нужно авторизироваться")
    
    # Создание сессии БД
    db = SessionLocal()
    allow_token = db.query(Token).filter(Token.token == token).first()
    if not allow_token:
        db.close()
        unauthorized("Некорректный токен")

    # Получение идентификатора пользователя из токена
    user_id = allow_token.user_id

    # Проверка, что пользователь не является отправителем сообщения
    sender_id = (
        db.query(Message.sender_id)
        .filter(Message.id == message_id)
        .scalar()
    )
    if sender_id == user_id:
        db.close()
        forbidden("Вы не можете ставить дислайк на своё сообщение")

    # Проверка, был ли уже установлен дислайк для данного сообщения
    existing_dislike = (
        db.query(Dislike)
        .filter(Dislike.user_id == user_id, Dislike.message_id == message_id)
        .first()
    )
    if existing_dislike:
        db.close()
        bad_request("Дислайк уже установлен")
    # Проверка, было ли сообщение удалено
    message = (
        db.query(Message)
        .filter(Message.id == message_id, Message.is_deleted == False)
        .first()
    )
    if not message:
        db.close()
        not_found("Сообщение не найдено")
    # Создание записи о дислайке
    dislike = Dislike(user_id=user_id, message_id=message_id, is_dislike=True)
    db.add(dislike)
    db.commit()
    # Закрытие сессии БД
    db.close()
    # Возвращаем статус успешной установки дислайка
    return {"detail": "Дислайк установлен"}
