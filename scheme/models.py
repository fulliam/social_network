import datetime
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, DateTime, Boolean

Base = declarative_base()

# модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

# схема для запроса на создание пользователя
class UserAuth(BaseModel):
    username: str
    password: str

# модель сообщения
class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    sender_id = Column(Integer)
    recipient_id = Column(Integer)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())
    edited_at = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)

# схема для запроса на создание сообщения
class MessageSend(BaseModel):
    recipient_id: int
    message: str    

# схема для запроса на обновление сообщения
class MessageUpdate(BaseModel):
    message: str    

# модель токена
class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    token = Column(String, index=True)
    secret = Column(String, index=True)
    user_id = Column(Integer)

# модель лайка для сообщений
class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    message_id = Column(String)
    is_like = Column(Boolean)

# модель дислайка для сообщений
class Dislike(Base):
    __tablename__ = "dislikes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    message_id = Column(String)
    is_dislike = Column(Boolean)    

# модель поста
class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(Integer)
    post = Column(String)
    likes_count = Column(Integer)
    dislikes_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now())
    edited_at = Column(DateTime, nullable=True)

# схема для запроса на создание поста
class PostSend(BaseModel):
    post: str

# модель реакции на пост
class PostReaction(Base):
    __tablename__ = "post_reactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    post_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    reaction_type = Column(String)

# схема для запроса на создание реакции на пост
class PostReactionCreate(BaseModel):
    type: str