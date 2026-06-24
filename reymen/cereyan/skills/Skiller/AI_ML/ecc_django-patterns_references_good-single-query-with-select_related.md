# Good - Single query with select_related
products = Product.objects.select_related('category').all()
for product in products:
    print(product.category.name)