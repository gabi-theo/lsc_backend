from datetime import datetime, timedelta
import secrets
import string
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import SlidingToken, UntypedToken
from rest_framework_simplejwt.exceptions import TokenError


class LongLiveSlidingToken(SlidingToken):
    token_type = "sliding"
    lifetime = timedelta(seconds=settings.LONG_LIVE_SLIDING_TOKEN_LIFETIME_SEC)


def set_value_to_cookie(response, key, value, expires=settings.SESSION_COOKIE_AGE):
    response.set_cookie(
        key=key,
        value=value,
        expires=expires,
        httponly=True,
    )


def set_token_to_header(response, token):
    response.headers["x-token"] = token


def map_to_bool(value):
    if value == "TRUE":
        return True
    elif value == "FALSE" or value == "0":
        return False
    elif value == "1":
        return True
    else:
        return None


def format_whised_make_up_times(
    wished_make_up_date,
    wished_make_up_min_time,
    wished_make_up_max_time,
):
    return (
        datetime.strptime(wished_make_up_date, "%Y-%m-%d").date(),
        datetime.strptime(wished_make_up_min_time, "%H:%M:%S").time(),
        datetime.strptime(wished_make_up_max_time, "%H:%M:%S").time(),
    )


def check_excel_format_in_request_data(request):
    if 'file' not in request.data:
        return Response({'error': 'File not provided'}, status=status.HTTP_400_BAD_REQUEST)

    excel_file = request.data['file']
    if not excel_file.name.endswith('.xls') and not excel_file.name.endswith('.xlsx'):
        return Response(
            {'error': 'Invalid file format. Please provide an Excel file.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


def random_password_generator():
    return ''.join(
        secrets.choice(
            string.ascii_letters + string.digits + string.punctuation
        ) for _ in range(12))


def generate_token_generic(jwt_lifetime_sec: int, **data) -> UntypedToken:
    token = UntypedToken()
    token.set_exp(lifetime=timedelta(seconds=jwt_lifetime_sec))
    for k, v in data.items():
        token[k] = v

    return token

def validate_token_generic(
    token: str, token_key: str, token_location: str, *data_keys: str
) -> dict:
    try:
        token = UntypedToken(token)
        token.verify()
    except TokenError:
        auth_error_msg = f"'{token_key}' token is invalid or expired."
    else:
        result = {}
        for key in data_keys:
            value = token.get(key)
            if not value:
                auth_error_msg = (
                    f"'{token_key}' token doesn't have '{key}' or value is empty"
                )
                break
            result[key] = value
        else:
            return result

    exc = AuthenticationFailed(auth_error_msg)
    exc.auth_header = f"{token_location} '{token_key}'"

    raise exc
