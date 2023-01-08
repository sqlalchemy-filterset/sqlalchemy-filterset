<span style="font-size: 65px; color: #7e56c2">**SQLAlchemy Filterset**</span>

<p align="left">
    <em>An easy way to filter, sort, paginate SQLAlchemy queries</em>
</p>

---
**Documentation**: <a href="https://idaproject.github.io/sqlalchemy-filterset/" target="_blank">https://sqlalchemy-filterset.github.io/sqlalchemy-filterset</a>

**Source Code**: <a href="https://github.com/idaproject/sqlalchemy-filterset" target="_blank">https://github.com/sqlalchemy-filterset/sqlalchemy-filterset</a>

---
This library offers a way to declaratively define filters on your database queries by creating a class that represents the filters you want to apply.
This class, called a FilterSet, can be used to filter a set of records in the database using SQLAlchemy.
It is typically used to allow users to search, filter, sort, paginate data in a web application.

The key features are:

* [X] Declaratively define filters.
* [X] Keep all of your filters in one place, making it easier to maintain and change them as needed.
* [X] Construct complex filtering conditions by combining multiple simple filters.
* [X] It offers a standard approach to writing database queries.
* [X] Reduce code duplication by allowing you to reuse the same filters in multiple places in your code.

## Installation

```bash
pip install sqlalchemy-filterset
```
Requirements: `Python 3.7+` `SQLAlchemy 1.4+`


## Basic Usage

<span style="color:red">todo: full example of a simple web application with description for each step.</span>

In the example provided, a FilterSet called ProductFilterSet is defined to filter records from a Product database model.
The ProductFilterSet class has several attributes, each of which is an instance of a Filter object.
Each Filter object is associated with a field in the Product model and a lookup expression function, which specifies how the filter should be applied to the query.

For example, the id attribute is a Filter object that is associated with the id field in the Product model.
The title attribute is a Filter object that is associated with the title field in the Product model.

When the ProductFilterSet is applied to a query, it modifies the query by adding WHERE clauses to it based on the filters that have been specified.
For example, if the title attribute is specified as "Apple", the query would be modified to only return records where the title field is "Apple".

The declarative style allows users to easily specify criteria for filtering the records that are returned from the database by simply setting the attributes of the ProductFilterSet class.
This can be more convenient and easier to understand than writing raw SQL queries, which can be more error-prone and difficult to maintain.

### Define a Model

```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    category = Column(Integer)
    is_active = Column(Boolean)

```

### Define a FilterSet

In a declarative style, we describe the attributes that will participate in filtering the query in the database:
```python
from sqlalchemy_filterset.filtersets import FilterSet
from sqlalchemy_filterset.filters import Filter, InFilter, RangeFilter, BooleanFilter


class ProductFilterSet(FilterSet):
    id = Filter(Product.id)
    ids = InFilter(Product.id)
    title = Filter(Product.title)
    price = RangeFilter(Product.price)
    category = InFilter(Product.category)
    is_active = BooleanFilter(Product.is_active)

```

```python

# Here full exmple
# Define a filter schema
# Write a base query
# Filter query
```



## License

This project is licensed under the terms of the MIT license.
