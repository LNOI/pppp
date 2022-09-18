
def try_float(input, default_value=0.0) -> float:
    try:
        return float(input)
    except (ValueError, TypeError) as e:
        return default_value

def try_int(input, default_value=0) -> int:
    try:
        return int(input)
    except (ValueError, TypeError) as e:
        return default_value