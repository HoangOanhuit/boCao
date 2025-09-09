import re
import time
import requests
import json
from datetime import datetime
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

URL = "https://s1apihd.com/wp-json/v1/app/truyen/bocao/run"  # Replace with real endpoint
PAYLOAD = {
    "user_id": "923763",
    "uuid": "B391A98E-E176-4FFB-954E-757C959D74A1",
    "versionIOS": "1",
    "method": "gold",
    "auth": "33295779ac154bb905221ec4600841ee",
    "activation_key": "",
    "email": "hoangphaile2@gmail.com",
    "truyen_id": "13419626",
    "registered": "2025-02-14 07:24:34",  # FIXED: dÃ¹ng timestamp cá»' Ä'á»‹nh
}  # Adjust per API
HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
    "user-agent": "TruyenHD/2.2 (com.vnvnads.TruyenHD; build:31; iOS 18.3.1) Alamofire/5.9.0",
    "accept-language": "vi-VN;q=1.0, en-VN;q=0.9",
}
DELAY = 0.05  # 50 ms


def sync_server_time():
    """Try to report server clock offset for better timing."""
    try:
        r = requests.head(URL, headers=HEADERS, timeout=5)
        server_time = parsedate_to_datetime(r.headers["Date"])
        offset = (server_time - datetime.now(timezone.utc)).total_seconds()
        print(f"[i] Server clock ahead by {offset:.3f}s")
    except Exception as e:
        print(f"[!] Failed to sync time: {e}")


def parse_wait_time(status_text):
    """Parse waiting time from Vietnamese status message.

    Handles both raw Vietnamese text and Unicode-escaped JSON strings.
    Returns wait time in seconds, or None if not found.
    """
    # First try to decode Unicode escapes if present
    try:
        # If it's a JSON-like string with Unicode escapes, decode it
        if '\\u' in status_text:
            decoded = status_text.encode('utf-8').decode('unicode_escape')
        else:
            decoded = status_text
    except:
        decoded = status_text

    # Remove HTML tags
    clean_text = re.sub(r"<[^>]+>", "", decoded)

    # Try multiple patterns for Vietnamese time units
    patterns = [
        # Standard Vietnamese
        r"(\d+)\s*(?:giây|giay)",  # seconds
        r"(\d+)\s*(?:phút|phut)",  # minutes
        r"(\d+)\s*(?:giờ|gio)",  # hours
        # Unicode escaped versions
        r"(\d+)\s*ph\\u00fat",  # \u00fat = ú
        r"(\d+)\s*gi\\u1edd",  # \u1edd = ờ
        # Corrupted encoding versions (from your original code)
        r"(\d+)\s*(?:giÃ¢y|phÃºt|giá»)",
        # English fallback
        r"(\d+)\s*(?:second|minute|hour)s?",
    ]

    for pattern in patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            matched_text = match.group(0).lower()

            # Determine unit and convert to seconds
            if any(unit in matched_text for unit in ['phút', 'phut', 'ph\\u00fat', 'phÃºt', 'minute']):
                return value * 60
            elif any(unit in matched_text for unit in ['giờ', 'gio', 'gi\\u1edd', 'giá»', 'hour']):
                return value * 3600
            else:  # seconds by default
                return value

    return None


def fire_request(session):
    """Send one POST request using persistent session.

    Returns tuple ``(success, wait_seconds)`` where ``wait_seconds`` is ``None`` if
    the response does not specify a waiting time.
    """

    try:
        resp = session.post(URL, json=PAYLOAD, timeout=5)
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]

        # Pretty print the JSON response for better readability
        try:
            data = resp.json()
            formatted_response = json.dumps(data, ensure_ascii=False, indent=2)
            print(f"{timestamp} POST {resp.status_code}:")
            print(formatted_response)
        except:
            print(f"{timestamp} POST {resp.status_code}: {resp.text}")

        data = resp.json()
        if data.get("error") == 0:
            return True, None

        status = data.get("status", "")
        wait_seconds = parse_wait_time(status)

        if wait_seconds:
            print(f"[i] Parsed wait time: {wait_seconds} seconds ({wait_seconds // 60}m {wait_seconds % 60}s)")

        return False, wait_seconds

    except Exception as e:
        print(f"[!] Request error: {e}")
        return False, None


def spam_loop():
    """Repeatedly send requests until success, adapting to wait messages."""

    session = requests.Session()
    session.headers.update(HEADERS)

    while True:
        start = time.time()
        success, wait_seconds = fire_request(session)
        if success:
            print("[+] Success! Stopping.")
            break

        if wait_seconds and wait_seconds > 1:
            # Server says to come back after X seconds; wait until ~1s before
            print(f"[i] Waiting {wait_seconds - 1} seconds before next attempt...")
            time.sleep(max(wait_seconds - 1, 0))

        elapsed = time.time() - start
        time.sleep(max(DELAY - elapsed, 0))


if __name__ == "__main__":
    sync_server_time()
    spam_loop()
