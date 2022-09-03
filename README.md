# Тестовое задание
- [Описание](#Описание)
- [Задание](#Задание)
- [Рекомендации](#Рекомендации)
- [Ссылки](#Ссылки)

## Описание
Репозиторий-заготовка для выполнения тестового задания для вступления в команду бэкенда. Призван погрузить сразу в веб-разработку с ORM и наработками внутри и вокруг проекта.

### Стек
- Язык программирования: [Python](https://www.python.org/downloads/) 3.9+
- ORM-система: [SQLAlchemy](https://www.sqlalchemy.org/) 1.4/2.0+
- Микро-фреймворк: [Flask](https://flask.palletsprojects.com/en/2.2.x/) 2.0+
- При участии: [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/index.html) и [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/stable/)
- А также: [Flask-Fullstack](https://github.com/niqzart/flask-fullstack)

### Начало и установка
1. Создать публичный fork репозитория
2. Склонировать репозиторий себе
3. Инициализировать субмодули (запускать в папке проекта):
```sh
git submodule init
git submodule update
```
4. Создать виртуальное окружение
5. Установить зависимости:
```sh
pip install -r requirements.txt
```
6. Запуск сервера:
```bash
make start
```
7. Проверить, документация работает: [http://localhost:5000/doc/](http://localhost:5000/doc/)

**Делать изменения в папке `__lib__` не нужно, коммитить их — тем более**


## Задание
Список задач(TODO) позователя:
* Имеет описание, категорию, дату выполения, время начала и завершения.
* Список возможных категорий для задач отдельный для каждого пользователя.
* Возможность получить список задач пользователя по конкретной дате.
* CRUD операции для задач и категорий задач.
* Категорию нельзя удалить, если она используется хотя бы в одной задаче.
* Пользователь должен быть авторизирован и может получать список только своих задач


## Рекомендации
### Flask-Fullstack
В проекте во всю мощь используется библиотека flask-fullstack (FFS), которая подгружена в проекте в виде submodule-я \_\_lib\_\_. В ней есть частичная документация, но вот пример использования вытащить из проекта не удалось. Стоит прочитать документацию в файлах:
- [Интерфейсы для БД](https://github.com/niqzart/flask-fullstack/blob/master/flask_fullstack/interfaces.py)
- [.database_searcher](https://github.com/niqzart/flask-fullstack/blob/master/flask_fullstack/mixins.py#L53)
- [.jwt_authorizer](https://github.com/niqzart/flask-fullstack/blob/master/flask_fullstack/mixins.py#L121)
- [ResourceController + его методы](https://github.com/niqzart/flask-fullstack/blob/master/flask_fullstack/restx.py#L23)

Понимание flask-restx и sqlalchemy сильно поможет в понимании ffs, уже с этими знаниями можно почитать информационный материал ниже:

<details>
  <summary>FFS: Порядок декораторов</summary>

  Все упаковщики запросов (`.a_response`, `.marshal_with`, `.marshal_list_with` или `.lister`) должны быть последним декоратором перед методами в `Resource`. Иначе вылет ошибки из других декораторов (`.argument_parser`, `.database_searcher`, `.jwt_authorizer`) будет либо подавлен, либо завёрнут в дополнительный слой ненужной вложенности, нарушая описанное в документации. Технически не относится к декораторам документирования, но ради лучшей читабельности и общности стоит везде складывать декораторы в одинаковом порядке.

  - все декораторы документации параметров запроса
  - все декораторы документации формата ответов
  - декораторы сессии (`with_session` или `with_auto_session`)
  - декоратор авторизации (`.jwt_authorizer`)
  - декоратор парсинга аргументов (`.argument_parser`)
  - декоратор(-ы) поиска объектов в бд (`.database_searcher`)
  - декоратор пост-обработки ответа (`.a_response`, `.marshal_with`, `.marshal_list_with` или `.lister`)
</details>

<details>
  <summary>FFS: Shortcut-ы для БД</summary>

  К объектам класса `sessionmaker` (ранее `Session`), которые по всему репозиторию обычно называются просто `session` добавлено несколько методов, упрощающих работу с логикой БД. По сути это простые shortcut-ы. Все их можно увидеть [тут](https://github.com/niqzart/flask-fullstack/blob/master/flask_fullstack/sqlalchemy.py#L15)

  Ко всем классам, наследующим Base, теперь добавляется набор полезных методов, которые могут значительно уменьшить объём работы. Они создаются и документированы [тут](https://github.com/niqzart/flask-fullstack/blob/master/flask_fullstack/sqlalchemy.py#L84)

</details>

<details>
  <summary>FFS: Модели для marshalling-а</summary>

  Реализуются через [Pydantic](https://github.com/samuelcolvin/pydantic), а точнее модификацию его модели из flask-fullstack: [PydanticModel](https://github.com/niqzart/flask-fullstack/blob/master/flask_fullstack/marshals.py#L426).
  
  Модели стоит создавать внутри тела класса, наследующего Base. Так её название заполнится автоматически и будет привязано к тому ORM-объекту, который она конвертирует. А для моделей, содержащих колонки БД всё ещё проще: в PydanticModel (и её потомках) объявлены статические методы для добавления к модели колонок (`column_model`). 
  
  Проще всего понять это через пример. Две модели внутри User, первая (IndexProfile) с id, username, bio и avatar, взятыми из соответствующих колонок, и вторая (FullProfile) со всеми полями первой и name, surname, patronymic и group, взятыми из соответствующих колонок:
  ```py
  IndexProfile = PydanticModel.column_model(id, username, bio, avatar)
  FullProfile = IndexProfile.column_model(name, surname, patronymic, group)
  ```

  - Модели объявляются в теле класса, наследующего Base!
  - Названия переменных нужно держать в `snake_case`, для json-а они будут автоматически конвертированы в `kebab-case`
  - Регистрировать новые модели не нужно, достаточно просто использовать их в методах, вроде `.marshal_with` или `.lister`
</details>

### Стиль кода
- **Будет проверяться**
- Соблюдение PEP8 обязательно
- Желательно не забывать Zen
- DRY приветствуется
- Автоматическое реформатирование рекомендуется
- Стоит поглядывать на стиль других файлов проекта

### Стиль git-а
- Желательно соблюдать [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
- Решить задачу в несколько коммитов
- Pull Request с описанием приветствуется

## Ссылки
### Общее
- [PEP8](https://www.python.org/dev/peps/pep-0008/)
- [pytest](https://docs.pytest.org/en/6.2.x/contents.html)

### Flask и расширения:
- [Flask-JWT-Extened](https://flask-jwt-extended.readthedocs.io/en/stable/)
- [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/index.html)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)

### SQLAlchemy:
- [Полный туториал](https://docs.sqlalchemy.org/en/14/tutorial/index.html)
- [Объявление таблиц в ORM](https://docs.sqlalchemy.org/en/14/tutorial/metadata.html#defining-table-metadata-with-the-orm)
- [Манипуляции с данными](https://docs.sqlalchemy.org/en/14/tutorial/orm_data_manipulation.html)
- [Отношения между таблицами](https://docs.sqlalchemy.org/en/14/orm/relationships.html)
- [Related object](https://docs.sqlalchemy.org/en/14/tutorial/orm_related_objects.html)
- [Multiple join paths](https://docs.sqlalchemy.org/en/14/orm/join_conditions.html#handling-multiple-join-paths)
