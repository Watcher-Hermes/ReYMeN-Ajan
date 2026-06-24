# Bulk delete
Product.objects.filter(stock=0).delete()
```