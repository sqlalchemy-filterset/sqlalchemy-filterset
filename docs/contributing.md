## Github
### Issues
Please create an issue to report a bug, request a feature or to simply ask a question.

### Pull Requests
Unless the pull request is a simple bugfix, please try to create an issue before starting on the implementation of your pull request.
This ensures that the potential feature is in alignment with project goals.
This also allows for feedback on the feature and potential help on where to start implementation wisely.

## Development
### Install dependencies

```bash
git clone git@github.com:sqlalchemy-filterse/sqlalchemy-filterset.git
cd sqlalchemy-filterset
poetry install
pre-commit install
```

### Tests
When adding additional features, please try to add tests that prove that your implementation works and is bug free.

Tests require a postgres database.

```bash
pytest
```


### Documentation
Documentation was built using mkdocs-material.
```bash
mkdocs serve
```

## Update package version
Run commitizen

```bash
poetry run cz bump --increment <MAJOR|MINOR|PATCH>
```

Push tag

```bash
git push && git push origin <tag_name>
```

Publish to pypi
```bash
POETRY_PYPI_TOKEN_PYPI=<TOKEN> poetry publish --build
```

Create release on Github
