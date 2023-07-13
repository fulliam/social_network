from fastapi import APIRouter, Depends
from utils.jwt import validate_token
from utils.sqlalchemy import SessionLocal
from utils.errors import unauthorized, forbidden, not_found
from fastapi.security import OAuth2PasswordBearer
from scheme.models import User, Message, MessageSend, MessageUpdate, Token, Like, Dislike
import uuid
import datetime

router = APIRouter(
    tags=["Messages"],
    prefix="/chat"
)
# Схема аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

@router.post("/messages")
async def create_message(message: MessageSend, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для отправки сообщения пользователю по user id
    """
    # Проверка валидности токена
    valid_token = validate_token(token)
    if not valid_token:
        unauthorized("Упс! Вам нужно авторизироваться")
    
    # Создание сессии БД
    db = SessionLocal()
    # Проверка наличия токена в БД
    allow_token = db.query(Token).filter(Token.token == token).first()
    if not allow_token:
        db.close()
        unauthorized("Некорректный токен")
    
    # Получение идентификатора пользователя из токена
    sender_id = allow_token.user_id

    # Генерация уникального идентификатора сообщения
    msg_id = str(uuid.uuid4())
    # Получение текущего времени
    time_now = datetime.datetime.now()
    # Создание объекта сообщения для сохранения в БД
    db_message = Message(id=msg_id,
                        sender_id=int(sender_id), 
                        recipient_id=int(message.recipient_id), 
                        message=str(message.message),
                        created_at=str(time_now))
    # Добавление сообщения в сессию БД
    db.add(db_message)
    # Фиксация изменений в БД
    db.commit()
    # Закрытие сессии БД
    db.close()
    # Возвращаем статус успешной отправки сообщения и все данные о сообщении
    return {
        "detail": "Сообщение отправлено!",
        "id": msg_id,
        "sender_id": sender_id,
        "recipient_id": message.recipient_id,
        "message": message.message,
        "created_at": time_now
    }


@router.get("/messages/{recipient_id}")
async def get_user_messages(recipient_id: int, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для получения всех входящий сообщений по user id
    """
    # Проверка валидности токена
    valid_token = validate_token(token)
    if not valid_token:
        unauthorized("Упс! Вам нужно авторизироваться")

    # Создание сессии БД
    db = SessionLocal()
    # Проверка наличия токена в БД
    allow_token = db.query(Token).filter(Token.token == token).first()
    if not allow_token:
        db.close()
        unauthorized("Некорректный токен")

    # Получение идентификатора пользователя из токена
    user_id = allow_token.user_id

    # Запрет на чтение чужих сообщений
    if user_id != recipient_id:
        db.close()
        forbidden("Вы можете читать только свои сообщения :)")

    # Получение всех сообщений для указанного получателя, включая проверку is_deleted
    messages = db.query(Message).filter(
        Message.recipient_id == recipient_id,
        Message.is_deleted == False
    ).all()

    # Получение уникальных идентификаторов отправителей
    sender_ids = list(set([message.sender_id for message in messages]))

    # Получение информации об отправителях сообщений
    senders = db.query(User).filter(User.id.in_(sender_ids)).all()

    # Получение информации о лайках и дислайках для каждого сообщения
    likes = db.query(Like).filter(Like.message_id.in_([message.id for message in messages])).all()
    dislikes = db.query(Dislike).filter(Dislike.message_id.in_([message.id for message in messages])).all()

    # Закрытие сессии БД
    db.close()

    # Создание словарей для хранения информации о лайках и дислайках по идентификаторам сообщений
    likes_by_message = {like.message_id: like.is_like for like in likes}
    dislikes_by_message = {dislike.message_id: dislike.is_dislike for dislike in dislikes}

    # Создание словаря для хранения имен отправителей по их идентификаторам
    sender_names = {sender.id: sender.username for sender in senders}

    # Формирование списка полученных сообщений
    received_messages = []
    for message in messages:
        sender_name = sender_names.get(message.sender_id)
        received_messages.append(
            {
                "message": message,
                "username": sender_name,
                "is_liked": likes_by_message.get(message.id),
                "is_disliked": dislikes_by_message.get(message.id),
            }
        )

    # Возвращаем все полученные сообщения
    return received_messages



@router.put("/messages/{message_id}")
async def update_message(message_id: str, data: MessageUpdate, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для изменения своих сообщений по message id
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
    sender_id = allow_token.user_id
    
    # Поиск сообщения в БД, включая проверку is_deleted
    db_message = db.query(Message).filter(
        Message.id == message_id,
        Message.sender_id == sender_id,
        Message.is_deleted == False
    ).first()
    if not db_message:
        db.close()
        not_found("Сообщение не найдено")
    
    # Запись обновлённого сообщения
    updated_message = data.message
    if updated_message:
        # Обновление поля message
        db_message.message = updated_message
        # Получение текущего времени
        db_message.edited_at = datetime.datetime.now()
        # Фиксация изменений в БД
        db.commit()
    # Закрытие сессии БД
    db.close()
    # Возвращаем статус успешного обновления сообщения
    return {"detail": "Сообщение обновлено"}

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для "удаления" своих сообщений по message id
    """
    # Проверка валидности токена
    valid_token = validate_token(token)
    if not valid_token:
        unauthorized("Упс! Вам нужно авторизироваться")
    
    # Создание сессии БД
    db = SessionLocal()
    # Проверка наличия токена в БД
    allow_token = db.query(Token).filter(Token.token == token).first()
    if not allow_token:
        db.close()
        unauthorized("Некорректный токен")
    
    # Получение идентификатора пользователя из токена
    sender_id = allow_token.user_id

    # Поиск сообщения в базе данных, включая проверку is_deleted
    db_message = db.query(Message).filter(
        Message.id == message_id,
        Message.sender_id == sender_id,
        Message.is_deleted == False
    ).first()
    if not db_message:
        db.close()
        not_found("Сообщение не найдено")
    
    # Установка флага `is_deleted` в True
    db_message.is_deleted = True
    # Фиксация изменений в БД
    db.commit()
    # Закрытие сессии БД
    db.close()
    # Возвращаем статус успешного удаления сообщения
    return {"detail": "Сообщение удалено"}