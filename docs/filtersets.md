
<span style="color:red">todo: check and rewrite</span>

<span style="color:red">todo: extend example, add example how to pass session</span>


## Overview

FilterSet is a class that modifies a database query.
When a FilterSet is applied to a query, it modifies the query by adding `WHERE` clauses to it based on the filters that have been specified.
This allows you to specify criteria for filtering the records that are returned from the database.
It is used by passing a session object and a query object.
The session object is used to execute the modified query, while the query object is the base query that the FilterSet modifies.

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

## Filter schema
The filter_schema is a dictionary that define which filters to apply to a FilterSet.
It has the following format: `{filter_name1: value1, filter_name2: value2}`, where field is the name of the field in the FilterSet and value is the value to use for filtering.

For example, to filter a ProductFilterSet by a minimum price of 1000, a maximum price of 5000, and only active products, you would use the following filter_schema:

```python
filter_params = {"price": (1000, 5000), "is_active": True}
```
It is convenient to use pydantic to define filter schema:
```python
from pydantic import BaseModel


class ProductFilterSchema(BaseModel):
    id: set[int] | None
    ids: set[int] | None
    title: str | None
    price: tuple[Price | None, Price | None] | None
    category: set[ProductCategory] | None
    is_active: bool | None

filter_schema = ProductFilterSchema(price=(1000, 5000), is_active=True)
filter_params = filter_schema.dict(exclude_unset=True)
```

## Filtering
To apply filtering, you can pass filter_params to the filter method of the FilterSet.

For example:
```python
from sqlalchemy import select


query = select(Product)
filter_set = ProductFilterSet(session, query)
result = filter_set.filter(filter_params)
```
The resulting sql:
```sql
select *
  from product
 where price >= 100
   and price <= 500
   and is_active is true;
```

## Counting
The count function of FilterSet is used to count the number of records in a database that match a set of filters.
The result will be an integer representing the count of the number of matching records.

For example:
```python
from sqlalchemy import select


query = select(Product)
filter_set = ProductFilterSet(session, query)
result = filter_set.count(filter_params)
```
The resulting sql:
```sql
select count(1)
  from product
 where price >= 100
   and price <= 500
   and is_active is true;
```

## Sync/Async support

There are two classes: `FilterSet` and `AsyncFilterSet`.
They both have the same `filter` and `count` methods that are used the same way, except that `AsyncFilterSet` is designed to be used in an asynchronous environment.

For example, the same ProductFilterSet with `AsyncFilterSet`:
```python

class ProductFilterSet(AsyncFilterSet):
    id = Filter(Product.id)

query = select(Product)
filter_set = ProductFilterSet(session, query)
result = await filter_set.filter(filter_params)
```
