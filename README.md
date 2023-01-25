<span style="font-size: 65px; color: #7e56c2">**SQLAlchemy Filterset**</span>

<p align="left">
    <em>An easy way to filter, sort, paginate SQLAlchemy queries</em>
</p>

[![codecov](https://codecov.io/gh/sqlalchemy-filterset/sqlalchemy-filterset/branch/main/graph/badge.svg)](https://codecov.io/gh/sqlalchemy-filterset/sqlalchemy-filterset)
[![PyPI version](https://badge.fury.io/py/sqlalchemy-filterset.svg)](https://badge.fury.io/py/sqlalchemy-filterset)
[![Downloads](https://pepy.tech/badge/sqlalchemy-filterset)](https://pepy.tech/project/sqlalchemy-filterset)
[![CodeQL](https://github.com/sqlalchemy-filterset/sqlalchemy-filterset/actions/workflows/codeql.yml/badge.svg)](https://github.com/sqlalchemy-filterset/sqlalchemy-filterset/actions/workflows/codeql.yml)
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/sqlalchemy-filterset?color=%2334D058">

---
**Documentation**: <a href="https://sqlalchemy-filterset.github.io/sqlalchemy-filterset/" target="_blank">https://sqlalchemy-filterset.github.io/sqlalchemy-filterset</a>

**Source Code**: <a href="https://github.com/sqlalchemy-filterset/sqlalchemy-filterset" target="_blank">https://github.com/sqlalchemy-filterset/sqlalchemy-filterset</a>

---
The library provides a convenient and organized way to filter your database records.
By creating a `FilterSet` class, you can declaratively define the filters you want to apply to your `SQLAlchemy` queries.
This library is particularly useful in web applications, as it allows users to easily search, filter, sort, and paginate data.

The key features are:

* [X] Declaratively define filters.
* [X] Keep all of your filters in one place, making it easier to maintain and change them as needed.
* [X] Construct complex filtering conditions by combining multiple simple filters.
* [X] It offers a standard approach to writing database queries.
* [X] Reduce code duplication by reusing the same filters in multiple places in your code.
* [X] Sync and Async support of modern SQLAlchemy.

## Installation

```bash
pip install sqlalchemy-filterset
```
Requirements: `Python 3.7+` `SQLAlchemy 1.4+`


## Basic Usage

In this example we specify criteria for filtering the database records
by simply setting the attributes of the `ProductFilterSet` class.
This can be more convenient and easier to understand than writing raw SQL queries, which
can be more error-prone and difficult to maintain.

### Define a FilterSet

```python
from sqlalchemy_filterset import FilterSet, Filter, RangeFilter, BooleanFilter

from myapp.models import Product


class ProductFilterSet(FilterSet):
    id = Filter(Product.id)
    price = RangeFilter(Product.price)
    is_active = BooleanFilter(Product.is_active)
```
### Define a FilterSchema
```python
import uuid
from pydantic import BaseModel


class ProductFilterSchema(BaseModel):
    id: uuid.UUID | None
    price: tuple[float, float] | None
    is_active: bool | None
```

### Usage
```python
# Connect to the database
engine = create_engine("postgresql://user:password@host/database")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Create the filterset object
filter_set = ProductFilterSet(session, select(Product))

# Define the filter parameters
filter_params = ProductFilterSchema(price=(10, 100), is_active=True)

# Apply the filters to the query
filtered_products = filter_set.filter(filter_params.dict())
```

This example will generate the following query:
```sql
select product.id, product.title, product.price, product.is_active
from product
where product.price >= 10
  and product.price <= 100
  and product.is_active = true;
```


## License

This project is licensed under the terms of the MIT license.
