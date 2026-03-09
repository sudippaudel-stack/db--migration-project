"""
Utility helper functions for data transformation and validation.
Contains common functions used across the migration tool.
"""

import re
from datetime import date, datetime
from typing import Any


def to_unix_ms(ts: datetime | date | None) -> int | None:
    """
    Convert datetime/date to Unix timestamp in milliseconds.

    Args:
        ts: datetime or date object to convert

    Returns:
        Unix timestamp in milliseconds or None
    """
    if ts is None:
        return None

    if isinstance(ts, datetime):
        return int(ts.timestamp() * 1000)
    elif isinstance(ts, date):
        # Convert date to datetime at midnight
        dt = datetime.combine(ts, datetime.min.time())
        return int(dt.timestamp() * 1000)

    return None


def parse_dob(raw: Any) -> date | None:
    """
    Parse date of birth from various string formats.

    Supports formats:
    - YYYY-MM-DD
    - MM/DD/YYYY
    - DD-MM-YYYY
    - YYYY/MM/DD

    Args:
        raw: Raw date string or value

    Returns:
        date object or None if parsing fails
    """
    if not raw:
        return None

    if isinstance(raw, date):
        return raw

    if isinstance(raw, datetime):
        return raw.date()

    # Try various date formats
    formats = [
        "%Y-%m-%d",      # 2024-01-15
        "%m/%d/%Y",      # 01/15/2024
        "%d-%m-%Y",      # 15-01-2024
        "%Y/%m/%d",      # 2024/01/15
        "%d/%m/%Y",      # 15/01/2024
        "%m-%d-%Y",      # 01-15-2024
    ]

    raw_str = str(raw).strip()

    for fmt in formats:
        try:
            return datetime.strptime(raw_str, fmt).date()
        except (ValueError, AttributeError):
            continue

    # If all formats fail, return None
    return None


def safe_float(val: Any) -> float | None:
    """
    Safely convert value to float.

    Args:
        val: Value to convert

    Returns:
        float value or None if conversion fails
    """
    if val is None:
        return None

    if isinstance(val, float):
        return val

    if isinstance(val, (int, bool)):
        return float(val)

    # Handle string conversion
    val_str = str(val).strip()
    if val_str == '' or val_str.lower() in ('none', 'null', 'n/a'):
        return None

    try:
        return float(val_str)
    except (ValueError, TypeError):
        return None


def safe_int(val: Any) -> int | None:
    """
    Safely convert value to integer.

    Args:
        val: Value to convert

    Returns:
        int value or None if conversion fails
    """
    if val is None:
        return None

    if isinstance(val, int):
        return val

    if isinstance(val, bool):
        return int(val)

    # Handle string conversion
    val_str = str(val).strip()
    if val_str == '' or val_str.lower() in ('none', 'null', 'n/a'):
        return None

    try:
        # Handle floats in strings
        return int(float(val_str))
    except (ValueError, TypeError):
        return None


def safe_bool(val: Any) -> bool | None:
    """
    Safely convert value to boolean.

    Args:
        val: Value to convert

    Returns:
        bool value or None if conversion fails
    """
    if val is None:
        return None

    if isinstance(val, bool):
        return val

    if isinstance(val, int):
        return bool(val)

    # Handle string conversion
    if isinstance(val, str):
        val_lower = val.strip().lower()
        if val_lower in ('1', 'true', 'yes', 'y', 't', 'on'):
            return True
        elif val_lower in ('0', 'false', 'no', 'n', 'f', 'off', ''):
            return False

    return None


def trim_varchar(val: Any, max_len: int) -> str | None:
    """
    Trim string to maximum length.

    Args:
        val: Value to trim
        max_len: Maximum length

    Returns:
        Trimmed string or None
    """
    if val is None:
        return None

    s = str(val)

    if len(s) > max_len:
        return s[:max_len]

    return s


def sanitize_ssn(ssn: str | None) -> str | None:
    """
    Sanitize SSN by removing non-numeric characters.

    Args:
        ssn: SSN string

    Returns:
        Sanitized SSN or None
    """
    if not ssn:
        return None

    # Remove all non-numeric characters
    sanitized = re.sub(r'\D', '', str(ssn))

    if not sanitized:
        return None

    return sanitized


def extract_ssn4(ssn: str | None) -> str | None:
    """
    Extract last 4 digits of SSN.

    Args:
        ssn: Full SSN string

    Returns:
        Last 4 digits or None
    """
    if not ssn:
        return None

    sanitized = sanitize_ssn(ssn)
    if not sanitized:
        return None

    # Return last 4 digits
    return sanitized[-4:] if len(sanitized) >= 4 else sanitized


def normalize_relation(relation: str | None) -> str | None:
    """
    Normalize relationship string to uppercase.

    Args:
        relation: Relationship string

    Returns:
        Normalized relationship or None
    """
    if not relation:
        return None

    return str(relation).strip().upper()


def normalize_gender(gender: str | None) -> str | None:
    """
    Normalize gender to single character uppercase.

    Args:
        gender: Gender string

    Returns:
        Normalized gender (M/F/O) or None
    """
    if not gender:
        return None

    gender_str = str(gender).strip().upper()

    # Map common values
    gender_map = {
        'M': 'M',
        'MALE': 'M',
        'MAN': 'M',
        'F': 'F',
        'FEMALE': 'F',
        'WOMAN': 'F',
        'O': 'O',
        'OTHER': 'O',
        'X': 'O',
    }

    return gender_map.get(gender_str, gender_str[0] if gender_str else None)


def validate_percentage(percentage: Any) -> float | None:
    """
    Validate percentage value (0-100).

    Args:
        percentage: Percentage value

    Returns:
        Valid percentage or None
    """
    val = safe_float(percentage)

    if val is None:
        return None

    # Ensure percentage is between 0 and 100
    if val < 0:
        return 0.0
    elif val > 100:
        return 100.0

    return val


def format_display_id(id_val: Any, prefix: str = "") -> str:
    """
    Format ID for display purposes.

    Args:
        id_val: ID value
        prefix: Optional prefix

    Returns:
        Formatted ID string
    """
    if id_val is None:
        return "N/A"

    if prefix:
        return f"{prefix}{id_val}"

    return str(id_val)


def truncate_text(text: str | None, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text for display.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if not text:
        return ""

    text_str = str(text)

    if len(text_str) <= max_length:
        return text_str

    return text_str[:max_length - len(suffix)] + suffix


def calculate_age(dob: date | None, reference_date: date | None = None) -> int | None:
    """
    Calculate age from date of birth.

    Args:
        dob: Date of birth
        reference_date: Reference date (defaults to today)

    Returns:
        Age in years or None
    """
    if not dob:
        return None

    if reference_date is None:
        reference_date = date.today()

    age = reference_date.year - dob.year

    # Adjust if birthday hasn't occurred this year
    if (reference_date.month, reference_date.day) < (dob.month, dob.day):
        age -= 1

    return age if age >= 0 else None


def is_valid_ssn(ssn: str | None) -> bool:
    """
    Check if SSN is valid (9 digits).

    Args:
        ssn: SSN string

    Returns:
        True if valid, False otherwise
    """
    if not ssn:
        return False

    sanitized = sanitize_ssn(ssn)

    if not sanitized:
        return False

    # SSN should be exactly 9 digits
    return len(sanitized) == 9


def chunk_list(items: list, chunk_size: int) -> list:
    """
    Split list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
