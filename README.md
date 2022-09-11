## Разработка

### Установка библиотеки

```shell
git clone git@github.com:idaproject/sqlalchemy-filterset.git
cd sqlalchemy-filterset
poetry install
pre-commit install
```

### Внесение изменений

Добавьте необходимые файлы в stage

```shell
git add .
```

Сделайте коммит при помощи commitizen

```shell
poetry run cz commit
```

Обновите версию в коде проекта и создайте новый git-тег при помощи commitizen

```shell
poetry run cz bump
```

Пуш тэгов

```shell
git push --tags
```
