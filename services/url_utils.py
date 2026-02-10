import re
from urllib.parse import urlparse

URL_REGEX = re.compile(
    r'((?:https?://|www\.)[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+)',
    re.IGNORECASE
)

MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}


def extract_url(text: str) -> str | None:
    match = URL_REGEX.search(text)
    if not match:
        return None

    url = match.group(1).rstrip('.,!?")]}')

    if len(url) > MAX_URL_LENGTH:
        return None

    if url.startswith("www."):
        url = "https://" + url

    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        return None

    if not parsed.netloc:
        return None

    return url


def extract_domain(url: str) -> str | None:
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return None

    try:
        # Normalize IDN (homograph protection)
        hostname = hostname.encode("idna").decode("ascii")
    except UnicodeError:
        return None

    return hostname.lower()
