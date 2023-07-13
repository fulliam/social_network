from fastapi import APIRouter, Depends
from utils.jwt import validate_token
from utils.sqlalchemy import SessionLocal
from utils.errors import unauthorized, not_found, bad_request, forbidden
from fastapi.security import OAuth2PasswordBearer
from scheme.models import Post, PostSend, PostReaction, PostReactionCreate, Token
import uuid
import datetime

router = APIRouter(
    tags=["Blog"],
    prefix="/blog"
)
# Схема аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

@router.post("/post")
async def create_post(post: PostSend, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для создания поста
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

    # Генерация уникального идентификатора для поста
    post_id = uuid.uuid4()

    # Создание объекта поста для сохранения в БД
    new_post = Post(
        id=post_id,
        user_id=sender_id,
        post=post.post,
        likes_count=0,
        dislikes_count=0,
        created_at=datetime.datetime.now(),
        edited_at=None
    )
    # Добавление поста в сессию БД
    db.add(new_post)
    # Фиксация изменений в БД
    db.commit()
    # Обновление автоматически сгенерированного идентификатора
    db.refresh(new_post)
    # Закрытие сессии БД
    db.close()
    # возвращаем статус успешного создания поста
    return {"detail": "Пост успешно создан", "post_id": post_id}


@router.get("/posts")
async def get_all_posts(token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для просмотра всех постов
    """
    # Проверка валидности токена
    valid_token = validate_token(token)
    if not valid_token:
        unauthorized("Упс! Вам нужно авторизироваться")

    # Создание сессии БД
    db = SessionLocal()

    # Получение всех постов из БД
    posts = db.query(Post).all()

    # Закрытие сессии БД
    db.close()

    # Преобразование списка постов в словари для возврата в ответе
    formatted_posts = []
    for post in posts:
        formatted_posts.append({
            "post_id": post.id,
            "user_id": post.user_id,
            "post": post.post,
            "likes_count": post.likes_count,
            "dislikes_count": post.dislikes_count,
            "created_at": post.created_at,
            "edited_at": post.edited_at,
        })
    # Возвращаем все посты
    return formatted_posts


@router.post("/post/{post_id}/reaction")
async def reaction_on_post(post_id: str, reaction: PostReactionCreate, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для реакции на пост,
    # реакция может быть только like или dislike  

    **если вы уже поставили like, то повторно поставить его уже нельзя,**  
    **но можно поставить dislike, тогда like обнулится и его снова можно будет поставить**  

    - **{"type": "like"}**
    - **{"type": "dislike"}**
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

    # Получение поста из БД
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        db.close()
        not_found("Пост не найден")

    # Проверка, оценивал ли пользователь пост ранее
    existing_reaction = db.query(PostReaction).filter(
        PostReaction.post_id == post_id,
        PostReaction.user_id == user_id
    ).first()

    if existing_reaction:
        # Если пользователь оценил пост ранее
        if existing_reaction.reaction_type == reaction.type:
            # Если оценка совпадает, возвращаем ошибку
            bad_request("Вы уже оценили этот пост")
        else:
            # Если оценка отличается, изменяем оценку на новую
            if existing_reaction.reaction_type == "like":
                post.likes_count -= 1
            elif existing_reaction.reaction_type == "dislike":
                post.dislikes_count -= 1

            db.delete(existing_reaction)

    # Запрет оценки своих постов
    if post.user_id == user_id:
        db.close()
        bad_request("Вы не можете оценивать свои посты")
                
    # Апдейт счётчика реакций
    if reaction.type == "like":
        post.likes_count += 1
    elif reaction.type == "dislike":
        post.dislikes_count += 1
    # Запись новой реакции
    new_reaction = PostReaction(
        user_id=user_id,
        post_id=post_id,
        reaction_type=reaction.type
    )
    # Добавление реакции в сессию БД 
    db.add(new_reaction)
    # Фиксация изменений в БД
    db.commit()
    # Закрытие сессии БД
    db.close()
    # Возвращаем статус успешной реакции
    return {"detail": f"Вы поставили {reaction.type} на пост с ID: {post_id}"}


@router.put("/post/{post_id}")
async def edit_post(post_id: str, updated_post: PostSend, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для редактирования своих постов  
    **чужие посты редактировать нельзя**
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

    # Получение поста из БД
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        db.close()
        not_found("Пост не найден")

    if post.user_id != user_id:
        # Пользователь пытается редактировать чужой пост
        db.close()
        forbidden("Вы можете редактировать только свои посты")

    # Обновление содержимого поста
    post.post = updated_post.post
    post.edited_at = datetime.datetime.now()

    # Фиксация изменений в БД
    db.commit()
    # Закрытие сессии БД
    db.close()

    # Возвращаем успешный статус
    return {"detail": f"Пост с ID {post_id} успешно обновлен"}


@router.delete("/post/{post_id}")
async def delete_post(post_id: str, token: str = Depends(oauth2_scheme)):
    """
    # Маршрут для удаления поста
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
    
    # Поиск поста в БД
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    if not post:
        db.close()
        not_found("Пост не найден")
    
    # Удаление поста
    db.delete(post)
    # Фиксация изменений в БД
    db.commit()
    # Закрытие сессии БД
    db.close()
    return {"detail": "Пост успешно удален"}

