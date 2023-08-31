# Django CTE Example

## About

This project demonstrates the usage of Common Table Expressions (CTE) in Django using the package [django-cte](https://github.com/dimagi/django-cte) and PostgreSQL.

## Installation

### Prerequisites:

* docker
* docker-compose
* python 3.11
* pipenv

Run:

```bash
docker-compose -f config/postgres/docker-compose.yml up -d
pipenv install
python manage.py migrate
python manage.py loaddata fixtures/data.json
python manage.py runserver 0:8000
```

Visit http://localhost:8000/ for project demonstration and example usage.

## Description

Suppose the given dataset:

| **#** | **Store ID** | **Store name**    | **Product name** | **Quantity** | **Cost** |
|:-----:|:------------:|:-----------------:|:----------------:|:------------:|:--------:|
| 1     | 1            | Apple Originals 1 | iPhone 12 Pro    | 1            | 1000.00  |
| 2     | 1            | Apple Originals 1 | MacBook Pro 13   | 3            | 2000.00  |
| 3     | 1            | Apple Originals 1 | AirPods Pro      | 2            | 280.00   |
| 4     | 2            | Apple Originals 2 | iPhone 12 Pro    | 2            | 1000.00  |
| 5     | 3            | Apple Originals 3 | iPhone 12 Pro    | 1            | 1000.00  |
| 6     | 3            | Apple Originals 3 | MacBook Pro 13   | 1            | 2000.00  |
| 7     | 3            | Apple Originals 3 | MacBook Air      | 4            | 1100.00  |
| 8     | 3            | Apple Originals 3 | iPhone 12        | 2            | 1000.00  |
| 9     | 3            | Apple Originals 3 | AirPods Pro      | 3            | 280.00   |
| 10    | 4            | Apple Originals 4 | iPhone 12 Pro    | 2            | 1000.00  |
| 11    | 4            | Apple Originals 4 | MacBook Pro 13   | 1            | 2500.00  |

How to find stores who's sales where better than the average sales across all stores?

```python
total_sales_cte = With(
    Sale.objects.values('store_id').annotate(
        total_sales=Sum('cost')
    ),
    name='total_sales_cte'
)

avg_sales_cte = With(
    total_sales_cte.queryset().with_cte(total_sales_cte).annotate(
        base=Value('1'),
        total_sales=total_sales_cte.col.total_sales
    ).values('base').annotate(
        avg_sales=Func(F("total_sales"), function="AVG")
    ),
    name='avg_sales_cte'
)

queryset = (
    avg_sales_cte.join(
        total_sales_cte.queryset(),
        total_sales__gt=avg_sales_cte.col.avg_sales
    ).with_cte(total_sales_cte).with_cte(avg_sales_cte)
)
```

Result:

| **Store ID** | **Total Sales** |
|:------------:|:---------------:|
| 3            | 5380.00         |
| 4            | 3500.00         |


Generated SQL:

```sql

WITH RECURSIVE "total_sales_cte" AS
  (SELECT "app_sale"."store_id",
          SUM("app_sale"."cost") AS "total_sales"
   FROM "app_sale"
   GROUP BY "app_sale"."store_id"),
               "avg_sales_cte" AS
  (WITH RECURSIVE "total_sales_cte" AS
     (SELECT "app_sale"."store_id",
             SUM("app_sale"."cost") AS "total_sales"
      FROM "app_sale"
      GROUP BY "app_sale"."store_id") SELECT 1 AS "base",
                                             AVG("total_sales_cte"."total_sales") AS "avg_sales"
   FROM "total_sales_cte")
SELECT "total_sales_cte"."store_id",
       "total_sales_cte"."total_sales" AS "total_sales"
FROM "total_sales_cte"
INNER JOIN "avg_sales_cte" ON "total_sales_cte"."total_sales" > ("avg_sales_cte"."avg_sales")
```