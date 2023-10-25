def time_not_logged_rule(user):
    return user is not None and user.is_active
