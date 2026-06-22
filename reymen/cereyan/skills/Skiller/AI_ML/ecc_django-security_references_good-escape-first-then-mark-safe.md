# GOOD: Escape first, then mark safe
def render_good(user_input):
    return mark_safe(escape(user_input))