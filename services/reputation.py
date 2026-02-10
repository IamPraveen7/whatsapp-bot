import asyncio
import base64
import httpx
from config import VT_API_KEY, REQUEST_TIMEOUT, GSB_API_KEY

VT_HEADERS = {"x-apikey": VT_API_KEY}
VT_BASE = "https://www.virustotal.com/api/v3"

UNKNOWN_SCORE = 15
MAX_SCORE = 40


def vt_url_id(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")


def score_from_stats(stats: dict) -> int:
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)

    score = malicious * 12 + suspicious * 6
    return min(MAX_SCORE, score)


async def virustotal_score(url: str) -> int:
    url_id = vt_url_id(url)

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:

            # 1. Try cached report
            r = await client.get(
                f"{VT_BASE}/urls/{url_id}",
                headers=VT_HEADERS,
            )

            if r.status_code == 200:
                attrs = r.json().get("data", {}).get("attributes", {})
                stats = attrs.get("last_analysis_stats")
                if stats:
                    return score_from_stats(stats)
                return UNKNOWN_SCORE

            # Rate limit or auth error
            if r.status_code in (401, 403, 429):
                return UNKNOWN_SCORE

            # 2. Submit URL
            submit = await client.post(
                f"{VT_BASE}/urls",
                headers=VT_HEADERS,
                data={"url": url},
            )

            if submit.status_code != 200:
                return UNKNOWN_SCORE

            analysis_id = submit.json().get("data", {}).get("id")
            if not analysis_id:
                return UNKNOWN_SCORE

            # 3. Fast polling (best-effort)
            for _ in range(5):
                await asyncio.sleep(2)

                report = await client.get(
                    f"{VT_BASE}/analyses/{analysis_id}",
                    headers=VT_HEADERS,
                )

                if report.status_code != 200:
                    continue

                attrs = report.json().get("data", {}).get("attributes", {})
                if attrs.get("status") == "completed":
                    return score_from_stats(attrs.get("stats", {}))

            return UNKNOWN_SCORE

    except (httpx.RequestError, httpx.TimeoutException):
        return UNKNOWN_SCORE

async def gsb_score(url: str) -> int:
    payload = {
        "client": {"clientId": "whatsapp-bot", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            r = await client.post(
                f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GSB_API_KEY}",
                json=payload
            )
            r.raise_for_status()
            return 40 if r.json().get("matches") else 0

    except (httpx.RequestError, httpx.HTTPStatusError):
        return 0

