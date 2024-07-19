from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
import jwt


def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=6),
        'iat': datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def jwt_authenticate(token) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        return user
    except (jwt.DecodeError, jwt.ExpiredSignatureError, User.DoesNotExist):
        return None