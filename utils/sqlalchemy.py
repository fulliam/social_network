from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_USER, DB_PASS, DB_HOST, DB_NAME

# Подключение к Базе Данных => БД
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
