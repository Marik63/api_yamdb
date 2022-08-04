## **Проект YaMDb:**

- Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles).
  Произведениям присваивается категория (Category), а так же жанр (Genre).
- Список категорий и жанров устанавливается, и может быть расширен администратором.
- Пользователи оставляют текстовые отзыввы (Review) и ставят оценку в диапазоне от 1 до 10.
- Из пользовательских оценок формируется усреднённая оценка произведения — рейтинг.
- На одно произведение пользователь может оставить только один отзыв.
- Другие пользователи могут оставлять комметарии (Commentary) к отзыву.

____

# Как запустить проект:

1) Клонировать репозиторий и перейти в него в командной строке:

`git clone https://github.com/anywindblows/api_yamdb/`

2) Cоздать и активировать виртуальное окружение:

`python -m venv venv`

`source venv/Scripts/activate`

3) Установить зависимости из файла requirements.txt:

`python -m pip install --upgrade pip`

`pip install -r requirements.txt`

4) Выполнить миграции:

`python3 manage.py migrate`

5) Заполнить базу данных, с помощью management комманды:

`python3 manage.py fill_db`

## **Эндпоинты для взаимодействия с ресурсами:**

```bash
  - api/v1/auth/signup/ (POST): Передаём email и username, получаем confirmation_code.
  - api/v1/auth/token/ (POST): Передаём username и confirmation_code, получаем token.

  - api/v1/categories/ (GET, POST, DELETE): Получаем список категорий. Администратор может добавить или удалить категорию.
  - api/v1/genres/ (GET, POST, DELETE): Получаем список жанров. Администратор может добавить или удалить жанр.
  
  - api/v1/titles/ (GET, POST): Получения списка всех произведений или добавления нового администратором.
  - api/v1/titles/{titles_id}/ (GET, PATCH, DELETE): Получение информации о произведении, частичное обновление информации или удаление произведения.

  - api/v1/titles/{title_id}/reviews/ (GET, POST): Получения списка всех отзывов или добавления нового.
  - api/v1/titles/{title_id}/reviews/{review_id}/ (GET, PATCH, DELETE): Полуение отзыва по id, частичное обновление или удаление отзыва по id.
  
  - api/v1/titles/{title_id}/reviews/{review_id}/comments/ (GET, POST): Получение списка всех комментариев или добавление комментария к отзыву.
  - api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/ (GET, PATCH, DELETE): Получение комментария к отзыву, частичное обновление или удаление комментария к отзыву.
  
  - api/v1/users/ (GET, POST): Получение списка всех пользователей или создание нового пользователя администратором.
  - api/v1/users/{username}/ (GET, POST, DELETE): Получение пользователя или изменение/удаление данных пользователя по username администратором.
  - api/v1/users/me/ (GET, PATCH): Получение, изменение данных своей учетной записи пользователем.
```

### Примеры запросов

| Тип запроса | Эндпоинт                        | Исходящие данные                                  | Ответ                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------|---------------------------------|---------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GET         | ```api/v1/categories/```        | *_________*                                       | [{ <br/> "count": 1, <br/> "next": "0", <br/> "previous": "0", <br/> "results": [ <br/> { <br/> "name": "Фильм", <br/> "slug": "film" <br/> } <br/>]                                                                                                                                                                                                                                   |
| POST        | ```api/v1/genres/```            | {<br/> "name": "комедия": "slug": "comedy"<br/> } | {<br/> "name": "комедия": "slug": "comedy"<br/> }                                                                                                                                                                                                                                                                                                                                      |
| GET         | ```api/v1/titles/```            | *________*                                        | [{ <br/> "count": 1, <br/> "next": "0", <br/> "previous": "0", <br/> "results": [ <br/> { <br/> "id": "1", <br/> "name": "Фильм", <br/> "year": "1982" <br/> "rating": "8" <br/> "description": "описание" <br/> "genre": [ <br/> { <br/> "name": "Комедия", <br/>"slug": "comedy" <br/> } <br/>]<br/> "category": [ <br/> { <br/> "name": "Фильм", <br/>"slug": "film" <br/> } <br/>] |                                                                                                                                                                                                                                                                                                                             |

## **Разработчики группового проекта:**

- Александр Кондратьев: https://github.com/anywindblows
- Дмитрий Пирогов:  https://github.com/Levayaruka
- Марат Хайрутдинов:   https://github.com/Marik63