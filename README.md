# API для создания, редактирования, удаления и оценки сообщений и постов  
## Чтобы протестировать его работу Вам необходимо:  
### Клонировать репозиторий  
`git clone`  
### Установить зависимости  
`pip instal -r requirements.txt`  
## Установить PostgreSQL  
### Создать базу данных  
**`bash` Вход под суперпользователем**  
**`sudo su postgres`**  
**Запуск psql**  
**`psql`**  
**Создать базу данных**  
**`CREATE DATABASE social_net;`**  
**Создать роль для базы данных**  
**`CREATE USER net_admin WITH LOGIN PASSWORD 'password';`**  
**Выдать все права на базу данных для роли**  
**`GRANT ALL PRIVILEGES ON DATABASE social_net TO net_admin;`**  
**Подключиться к базе данных**  
**`\c social_net`**  
**Подключить расширение uuid для базы данных**  
**`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`**  
### Создать в корневом каталоге репозитория файл .env  
**Содержимое файла .env:**  
*ALGORITHM = HS256*  
*SECRET_KEY = mysecretkey*  
*DB_USER = net_admin*  
*DB_PASS = password*  
*DB_HOST = localhost*  
*DB_PORT = 5432*  
*DB_NAME = social_net*  
### Создать таблицы  
>*из корневого каталога репозитория*  
**`python3 create_table.py`**  
### Запустить API  
>*из корневого каталога репозитория*  
**`python3 API.py`**  
## Открыть документацию Swagger или воспользоваться curl-запросами  
`http://127.0.0.1:5050/docs`  
# Вы великолепны!