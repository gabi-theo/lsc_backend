from datetime import datetime


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