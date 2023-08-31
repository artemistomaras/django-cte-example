import sqlparse
from django.db.models import Sum, F, Func, Value
from django.shortcuts import render
from django_cte import With

from app.models import Sale


def index(request):
    sales = Sale.objects.select_related('product', 'store').all()

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

    query = sqlparse.format(str(queryset.query), reindent=True, keyword_case='upper')

    context = {
        'sales': sales,
        'query': query,
        'queryset': queryset
    }

    return render(request, "app/index.html", context)
