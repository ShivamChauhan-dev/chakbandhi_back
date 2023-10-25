from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken


def blacklist_user_refresh_tokens(user):
    tokens = OutstandingToken.objects.filter(user=user)
    for token in tokens:
        token = RefreshToken(token.token)
        token.blacklist()
