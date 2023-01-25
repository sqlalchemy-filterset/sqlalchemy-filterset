## Overview

`FilterSet` is a class that modifies a database query by adding `where` clauses to it based on specified filters.
To use it, create an instance of `FilterSet` class and define filters.
To apply the filtering to a query, pass the session and query to the filter method of the `FilterSet` instance.

## Workflow

``` mermaid
sequenceDiagram
    participant User
    participant App
    participant Database
    User->>App: Send request with filter parameters
    App->>App: Retrieve User Filter Parameters.<br> Apply Parameters to FilterSet and Construct Query
    App->>Database: Execute Query
    Database-->>App: Send Results
    App-->>User: Display Results
```

Example `FilterSet`:
```python
from sqlalchemy_filterset import (
    FilterSet,
    BooleanFilter,
    Filter,
    InFilter,
    RangeFilter,
)


class ProductFilterSet(FilterSet):
    id = Filter(Product.id)
    ids = InFilter(Product.id)
    title = Filter(Product.title)
    price = RangeFilter(Product.price)
    category = InFilter(Product.category)
    is_active = BooleanFilter(Product.is_active)

```

## Filter schema
Filter schema is a dictionary that defines the parameters for filtering a database query using a `FilterSet`.
It has the format of `{filter_name: value}`, where `filter_name` is the name of the field in
the `FilterSet` and value is the value to use for filtering.
However, different filters may have different formats ([see the filters description](/sqlalchemy-filterset/filters/)).

Using pydantic to define the filter schema is a convenient way to ensure the proper format and validation of the filter parameters.




For example, to filter the `ProductFilterSet` by active products, a minimum price of 1000, a maximum price of 5000, use the following filter_schema:
=== "dict"
    ```python
    filter_params = {"price": (1000, 5000), "is_active": True}
    ```

=== "pydantic"
    ```python
    from pydantic import BaseModel


    class ProductFilterSchema(BaseModel):
        id: int | None
        ids: set[int] | None
        title: str | None
        price: tuple[Price | None, Price | None] | None
        category: set[ProductCategory] | None
        is_active: bool | None

    filter_schema = ProductFilterSchema(price=(1000, 5000), is_active=True)
    filter_params = filter_schema.dict(exclude_unset=True)
    ```

    !!! info "Note: Using exclude_unset=True"

        - When the `exclude_unset=True` parameter is used in the `dict()` method,
        fields that were not explicitly set when creating the model
        are excluded from the returned dictionary.
        This is useful in this example because it means that only the attributes
        that have been set in the `filter_schema` object are included in the `filter_params` dictionary.
        In this case, the `filter_schema` object only has three attributes set: `price`,
        `is_active`, and `category`, so when `exclude_unset=True`,
        only these three attributes are included in the `filter_params` dictionary,
        and the other attributes with `None` value (`id`, `ids`, `title`) are excluded.
        This way, the query only filters by the passed parameters,
        and the `None` parameters will not affect it.

## Filtering
To apply filtering, you can pass `filter_params` to the filter method of the `FilterSet`.

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
The count function of `FilterSet` is used to count the number of records in a database that match a set of filters.
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
They both have the same `filter` and `count` methods that are used the same way, except that
`AsyncFilterSet` is designed to be used in an asynchronous environment.

For example, the same `ProductFilterSet` with `AsyncFilterSet`:

```python
class ProductFilterSet(AsyncFilterSet):
    id = Filter(Product.id)

query = select(Product)
filter_set = ProductFilterSet(session, query)
result = await filter_set.filter(filter_params)
```
