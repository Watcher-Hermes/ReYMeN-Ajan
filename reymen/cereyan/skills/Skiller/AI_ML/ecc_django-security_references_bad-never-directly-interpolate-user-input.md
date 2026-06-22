# BAD: Never directly interpolate user input
def get_user_bad(username):
    return User.objects.raw(f'SELECT * FROM users WHERE username = {username}')  # VULNERABLE!