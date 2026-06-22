# Step 4: Add to cart
        response = client.post(reverse('cart:add'), {
            'product_id': product.id,
            'quantity': 1,
        })
        assert response.status_code == 302