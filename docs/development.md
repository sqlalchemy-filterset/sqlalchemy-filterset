### Install dependencies

```shell
git clone git@github.com:idaproject/sqlalchemy-filterset.git
cd sqlalchemy-filterset
poetry install
pre-commit install
```

### Documentation
```shell
mkdocs serve
```

### Develop

Add files to stage

```shell
git add .
```

Commit with commitizen

```shell
poetry run cz commit
```

Update project version and create new git-tag with commitizen

```shell
poetry run cz bump
```

Push tags

```shell
git push --tags
```
