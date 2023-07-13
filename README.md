# REST API для создания, редактирования, удаления и оценки сообщений и постов  
## Технологии
![Python](https://img.shields.io/badge/python_3.11-3670A0?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-005571?style=for-the-badge)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
## Чтобы протестировать его работу Вам необходимо:  
### Клонировать репозиторий  
```bash
`git clone https://github.com/fulliam/social_network.git`  
```
### Установить зависимости  
```bash
`pip instal -r requirements.txt`  
```
## Установить PostgreSQL  
### Создать базу данных  
**Вход под суперпользователем**  
```bash
**`sudo su postgres`**  
```
**Запуск psql**  
```bash
**`psql`**  
```
**Создать базу данных**  
```bash
**`CREATE DATABASE social_net;`**  
```
**Создать роль для базы данных**  
```bash
**`CREATE USER net_admin WITH LOGIN PASSWORD 'password';`**  
```
**Выдать все права на базу данных для роли**  
```bash
**`GRANT ALL PRIVILEGES ON DATABASE social_net TO net_admin;`**  
```
**Подключиться к базе данных**  
```bash
**`\c social_net`**  
```
**Подключить расширение uuid для базы данных**  
```bash
**`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`**  
```
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
```bash
**`python3 create_table.py`**  
```
### Запустить API  
>*из корневого каталога репозитория*  
```bash
**`python3 API.py`**  
```
## Открыть документацию Swagger или воспользоваться curl-запросами  
`http://127.0.0.1:5050/docs`  
# Вы великолепны!