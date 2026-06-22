# Bad - N+1 queries
products = Product.objects.all()
for product in products:
    print(product.category.name)  # Separate query for each product