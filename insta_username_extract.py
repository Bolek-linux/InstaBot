import re


def is_valid_instagram_username(username: str) -> bool:
    """
    Checks if a string adheres to Instagram's username rules.

    According to Instagram's policies, a username must be between 1 and 30
    characters long. It can only contain letters, numbers, periods (.),
    and underscores (_). It cannot start or end with a period, nor can it
    contain consecutive periods.

    Args:
        username (str): The username string to validate.

    Returns:
        bool: True if the username is valid, False otherwise.
    """
    # 1. Check length constraints (1 to 30 characters).
    if not 1 <= len(username) <= 30:
        return False

    # 2. Check for invalid start or end characters (period).
    if username.startswith('.') or username.endswith('.'):
        return False

    # 3. Use regex to ensure only allowed characters are present and check for
    #    the consecutive periods rule, which regex doesn't easily cover.
    allowed_chars_pattern = re.compile(r"^[a-zA-Z0-9_.]+$")
    if not allowed_chars_pattern.match(username) or '..' in username:
        return False

    return True


def extract_instagram_username(input_string: str) -> str | None:
    """
    Extracts and validates an Instagram username from a URL or a raw string.

    This function handles various Instagram URL formats (e.g., profiles,
    live broadcasts, posts) and also validates direct username strings,
    which may or may not include an '@' prefix.

    Args:
        input_string (str): The full Instagram URL or a potential username string.

    Returns:
        str | None: The validated username if found, otherwise None.
    """
    # This regex captures the username from common Instagram URL patterns.
    # It looks for the string between "instagram.com/" and the next "/" or
    # the end of the string, which is where the username is consistently located.
    url_pattern = re.compile(
        r"^(?:https?://)?(?:www\.)?instagram\.com/(?P<username>[a-zA-Z0-9_.]+)"
    )

    match = url_pattern.match(input_string)

    potential_username = ""

    if match:
        # If the input is a URL that matches the pattern, extract the named group.
        potential_username = match.group("username")
    else:
        # If not a URL, treat the entire input as a potential username.
        # Remove the '@' prefix if it exists.
        potential_username = input_string.lstrip('@')

    # Regardless of the source, validate the potential username against the rules.
    if is_valid_instagram_username(potential_username):
        return potential_username

    # Return None if no valid username can be derived from the input string.
    return None
