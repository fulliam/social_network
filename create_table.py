import psycopg2
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

# подключение к базе данных
conn = psycopg2.connect(
    user = DB_USER,
    password = DB_PASS,
    host = DB_HOST,
    port = DB_PORT,
    database = DB_NAME,
)

# создание курсора
cursor = conn.cursor()

# создание таблицы "users"
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR UNIQUE,
        password_hash VARCHAR
    )
""")

# создание таблицы "messages"
cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id UUID DEFAULT uuid_generate_v4() UNIQUE PRIMARY KEY,
        sender_id INTEGER,
        recipient_id INTEGER,
        message VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        edited_at VARCHAR NULL,
        is_deleted BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (sender_id) REFERENCES users (id),
        FOREIGN KEY (recipient_id) REFERENCES users (id)
    )
""")

# создание таблицы "tokens"
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        token VARCHAR,
        secret VARCHAR,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
""")

# создание таблицы "likes"
cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        message_id UUID DEFAULT uuid_generate_v4(),
        is_like BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (message_id) REFERENCES messages (id)
    )
""")

# создание таблицы "dislikes"
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dislikes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        message_id UUID DEFAULT uuid_generate_v4(),
        is_dislike BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (message_id) REFERENCES messages (id)
    )
""")

# создание таблицы "posts"
cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        user_id INTEGER,
        post TEXT,
        likes_count INTEGER,
        dislikes_count INTEGER,
        created_at VARCHAR,
        edited_at VARCHAR,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
""")

# создание таблицы "post_reactions"
cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_reactions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        post_id UUID DEFAULT uuid_generate_v4() REFERENCES posts(id),
        reaction_type VARCHAR
    )
""")

# сохранение изменений в базе данных
conn.commit()
print("Таблицы успешно созданы")
# закрытие курсора и соединения
cursor.close()
conn.close()