![Изображение](https://yastatic.net/q/logoaas/v2/Яндекс.svg?circle=white&color=fff&first=black) ![Изображение](https://yastatic.net/q/logoaas/v2/Практикум.svg?color=fff)

# YaMDb
### Описание
YaMDb собирает **отзывы** пользователей на **произведения**. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

Произведения делятся на **категории**, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»).

Произведению может быть присвоен **жанр** из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»).

Добавлять произведения, категории и жанры может только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые **отзывы** и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — **рейтинг** (целое число). На одно произведение пользователь может оставить только один отзыв.

Пользователи могут оставлять **комментарии** к отзывам.

Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.
### Технологии
Python 3.9
Django 2.2.16
Django Rest Framework 3.12.4
JWT
Docker
PostgreSQL
Gunicorn
Nginx
### Запуск проекта
1. Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Gashev1989/infra_sp2.git
```

```
cd api_yamdb
```

2. Cоздать файл виртуального окружения .env в директории infra/ по образцу в env.example:

```
cd infra/
```
```
touch .env
```
Файл вирутального окружения должен содержать:
```
DB_ENGINE=движок базы данных
DB_NAME=имя базы данных
POSTGRES_USER=логин для подключения к базе данных
POSTGRES_PASSWORD=пароль для подключения к БД
DB_HOST=название сервиса (контейнера)
DB_PORT=порт для подключения к БД
SECRET_KEY='секретный ключ проекта'
```

3. Запустить проект:

```
docker-compose up -d --build
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
4. Заполнить базу данными:

```
docker-compose exec web python manage.py loaddata fixtures.json
```

5. Открыть документацию проекта:

```
http://127.0.0.1:8000/redoc/
```
***

### Регистрация:

```
POST http://127.0.0.1:8000/api/v1/auth/signup/
```
тело запроса:
```
{
    "email": "user@example.com",
    "username": "string"
}
```
после запроса на указанную почту придет ключ, для получения токена

### Получение JWT-токена
```
http://127.0.0.1:8000/api/v1/auth/token/
```
тело запроса:
```
{
    "username": "string",
    "confirmation_code": "string"
}
```
### Другие примеры запросов:


#### Получение списка всех произведений:

```
GET http://127.0.0.1:8000/api/v1/titles/
```
вернет ответ в формате JSON:
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "string"
        }
      ],
      "category": {
        "name": "string",
        "slug": "string"
      }
    }
  ]
}
```

#### Частичное обновление информации о произведении:

```
PATCH http://127.0.0.1:8000/api/v1/titles/{titles_id}/
```
тело запроса:
```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```

#### Добавление нового отзыва:

```
POST http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/
```
тело запроса:
```
{
    "text": "string",
    "score": 1
}
```

#### Частичное обновление отзыва по id:

```
PUTCH http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/
```
тело запроса:
```
{
  "text": "string",
  "score": 1
}
```
### Авторы
- [Александр Батанов](https://github.com/AlexBatanov) в роли тимлида
- [Константин Гашев](https://github.com/Gashev1989) в роли разработчика
- [Олег Исаев](https://github.com/oisaev) в роли разработчика
