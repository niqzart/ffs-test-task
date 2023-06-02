# Тестовое задание
- [Описание](#Описание)
- [Задание](#Задание)
- [Рекомендации](#Рекомендации)
- [Ссылки](#Ссылки)

## Описание
Репозиторий-заготовка для выполнения тестового задания для вступления в команду бэкенда. Призван погрузить в стек проекта, познакомить с используемыми библиотеками, в том числе внутрипроектными.

### Стек
- Язык программирования: [Python](https://www.python.org/downloads/) 3.9+
- ORM-система: [SQLAlchemy](https://www.sqlalchemy.org/) 1.4/2.0+
- Микро-фреймворк: [Flask](https://flask.palletsprojects.com/en/2.2.x/) 2.0+
- ORM-Плагин: [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/) 3.0+
- При участии: [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/index.html)
- А также: [Flask-Fullstack](https://github.com/niqzart/flask-fullstack) 0.4.8

### Начало и установка
1. Создать публичный fork репозитория
2. Склонировать репозиторий себе
3. Создать виртуальное окружение **на python 3.9**
4. Установить зависимости:
```sh
pip install -r requirements.txt
```
5. Запусить файл `app.py`, можно создать Run Configuration на его запуск
6. Проверить, документация работает: [http://localhost:5000/doc/](http://localhost:5000/doc/)

## Задание
Реализовать API TODO-листа с названием, категорией, началом и концом.

## Рекомендации
### Flask-Fullstack
В проекте во всю мощь используется библиотека flask-fullstack (FFS). В ней есть частичная документация, но вот пример использования вытащить из проекта не удалось. Стоит прочитать документацию в файлах:
- [Интерфейсы для БД](https://github.com/niqzart/flask-fullstack/blob/d54696b1b982015eb64790174d42bd21f7811a46/flask_fullstack/base/interfaces.py)
- [.database_searcher](https://github.com/niqzart/flask-fullstack/blob/d54696b1b982015eb64790174d42bd21f7811a46/flask_fullstack/base/mixins.py#L48)
- [.jwt_authorizer](https://github.com/niqzart/flask-fullstack/blob/d54696b1b982015eb64790174d42bd21f7811a46/flask_fullstack/base/mixins.py#L96)
- [ResourceController + его методы](https://github.com/niqzart/flask-fullstack/blob/d54696b1b982015eb64790174d42bd21f7811a46/flask_fullstack/restx/controller.py)

Никто не запрещает читать код репозитория внутри проекта, где используется эта библиотека: [xi.backend](https://github.com/xi-effect/xi.backend)

Знание flask-restx и sqlalchemy сильно поможет в понимании ffs, уже с этими знаниями можно почитать информационный материал ниже:

<details>
  <summary>FFS: Порядок декораторов</summary>

  Все упаковщики запросов (`.a_response`, `.marshal_with`, `.marshal_list_with` или `.lister`) должны быть последним декоратором перед методами в `Resource`. Иначе вылет ошибки из других декораторов (`.argument_parser`, `.database_searcher`, `.jwt_authorizer`) будет либо подавлен, либо завёрнут в дополнительный слой ненужной вложенности, нарушая описанное в документации. Технически не относится к декораторам документирования, но ради лучшей читабельности и общности стоит везде складывать декораторы в одинаковом порядке.

  - все декораторы документации параметров запроса
  - все декораторы документации формата ответов
  - декоратор авторизации (`.jwt_authorizer`)
  - декоратор парсинга аргументов (`.argument_parser`)
  - декоратор(-ы) поиска объектов в бд (`.database_searcher`)
  - декоратор пост-обработки ответа (`.a_response`, `.marshal_with`, `.marshal_list_with` или `.lister`)
</details>

<details>
  <summary>FFS: Shortcut-ы для БД</summary>

  К объекту `db.session` добавлено несколько методов, упрощающих работу с логикой БД. По сути это простые shortcut-ы. Все их можно увидеть [тут](https://github.com/niqzart/flask-fullstack/blob/93d3c6696c33171315c078ab88c68ca7f7094361/flask_fullstack/utils/sqlalchemy.py#L21)

  Ко всем классам, наследующим `Base` (именно `Base` из `common`, не `db.Model`!) теперь добавляется набор полезных методов, которые могут значительно уменьшить объём работы. Они создаются и документированы [тут](https://github.com/niqzart/ffs-test-task/blob/main/common/config.py#L67)

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

<details>
  <summary>FFS: SocketIO</summary>

  Частично задокументированно [внутри проекта](https://github.com/xi-effect/xieffect-backend/pull/110), более отделённая документация появится позже...

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
- Pull Request с мини-описанием приветствуется

## Ссылки
### Общее
- [PEP8](https://www.python.org/dev/peps/pep-0008/)
- [pytest](https://docs.pytest.org/en/6.2.x/contents.html)

### Flask и расширения:
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/)
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
