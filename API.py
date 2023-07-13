import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scheme.models import User
from routes import auth
from routes.messages import messages, messages_feedback
from routes.posts import posts
from utils.sqlalchemy import SessionLocal

# Инициализация приложения
app = FastAPI(
    title='Social Network',
    version='1.0.0'
)

# Подключение маршрутов
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(messages_feedback.router)
app.include_router(posts.router)

# Настройки CORS
origins = [
    "http://localhost:8080",
    "http://localhost:8080/",
    "http://192.168.0.4:8080",
    "http://192.168.0.4:8080/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users", tags=["Users"])
async def read_users():
    """
    # Маршрут для получения списка всех пользователей
    """
    # Создание сессии БД
    db = SessionLocal()
    # Получение всех пользователей из БД
    users = db.query(User).all()
    # Закрытие сессии БД
    db.close()
    # Возвращаем id и имена всех пользователей
    return [{"id": user.id, "username": user.username} for user in users]

# uvicorn API:app --reload --port 9999

if __name__ == '__main__':
    uvicorn.run(
        'API:app', port=5050, host='127.0.0.1',
        reload=True)
       