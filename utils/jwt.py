import jwt
from config import ALGORITHM, SECRET_KEY

# Функция для создания jwt токена
def create_access_token(username):
    payload = {"sub": username}
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)  

# Функция для проверки jwt токена
def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return True
    except:
        return False