from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from .models import BlackListTokenAccess
import jwt


def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=6),
        'iat': datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def jwt_decode(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])


def jwt_authenticate(token) -> User:
    # Check if token is not in BlackList
    try:
        db_token = BlackListTokenAccess.objects.get(token=token)
        if db_token is not None:
            print("TOKEN IS INVALID")
            return None
    except:
        try:
            payload = jwt_decode(token)
            user = User.objects.get(id=payload['user_id'])
            return user
        except (jwt.DecodeError, jwt.ExpiredSignatureError, User.DoesNotExist):
            return None