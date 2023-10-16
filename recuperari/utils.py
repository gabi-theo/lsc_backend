from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from datetime import timedelta
from rest_framework_simplejwt.tokens import SlidingToken


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
