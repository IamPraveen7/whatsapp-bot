import ipaddress
import tldextract
from urllib.parse import urlparse
import re

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "lnkd.in", "cutt.ly"
}

SUSPICIOUS_TLDS = {
    "xyz", "top", "tk", "click", "work", "support"
}

CREDENTIAL_KEYWORDS = {
    "login", "verify", "update", "secure", "account", "signin"
}

def is_ip_domain(domain: str) -> bool:
    try:
        domain = domain.strip("[]")
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        return False


def heuristic_score(url: str) -> int:
    score = 0
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    path = parsed.path.lower()

    ext = tldextract.extract(domain)
    registered_domain = f"{ext.domain}.{ext.suffix}"

    # 1. URL shortener
    if registered_domain in SHORTENERS:
        score += 20

    # 2. Subdomain abuse (ignore common infra domains)
    subdomain_parts = [
        s for s in ext.subdomain.split(".")
        if s not in {"www", "mail", "api"}
    ]
    if len(subdomain_parts) >= 3:
        score += 15

    # 3. IP-based URL
    if is_ip_domain(domain):
        score += 30

    # 4. Suspicious or punycode TLD
    if ext.suffix in SUSPICIOUS_TLDS or "xn--" in ext.suffix:
        score += 20

    # 5. Credential harvesting paths (token-based)
    path_tokens = re.split(r"[^a-z0-9]", path)
    if any(token in CREDENTIAL_KEYWORDS for token in path_tokens):
        score += 15

    return score
