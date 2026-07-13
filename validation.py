import re

# Regex patterns
LOCATION_RE = re.compile(r'^[A-Z0-9]{10}$')  # 10 uppercase alphanumeric characters
ROLL_RE = re.compile(r'^[A-Za-z0-9]{9}$')    # 7 alphanumeric characters

ERROR_MSG_LOCATION = "EL FORMATO NO COINCIDE CON EL DE LA UBICACIÓN. REINTENTE"
ERROR_MSG_ROLL = "EL ARTICULO NO CUMPLE CON EL FORMATO. REINTENTE."


def validate_location(code: str) -> bool:
    """Validate location code format: exactly 10 uppercase alphanumeric characters."""
    if not isinstance(code, str):
        return False
    return bool(LOCATION_RE.match(code))


def validate_roll(code: str) -> bool:
    """Validate roll code format: exactly 7 alphanumeric characters."""
    if not isinstance(code, str):
        return False
    return bool(ROLL_RE.match(code))
