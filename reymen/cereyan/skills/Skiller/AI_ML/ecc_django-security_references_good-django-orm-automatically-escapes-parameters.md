# GOOD: Django ORM automatically escapes parameters
def get_user(username):
    return User.objects.get(username=username)  # Safe