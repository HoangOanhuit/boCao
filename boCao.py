import re
import time
import json
import requests
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://s1apihd.com/wp-json/v1/app/truyen/bocao/run"
PAYLOAD = {
    "user_id": "923763",
    "uuid": "B391A98E-E176-4FFB-954E-757C959D74A1",
    "versionIOS": "1",
    "method": "gold",
    "auth": "6dfc199d1c8b7e86465d359fc8aa470f",
    "activation_key": "",
    "email": "hoangphaile2@gmail.com",
    "truyen_id": "13418960",
    "registered": "2025-02-14 07:24:34",
}
HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
    "user-agent": "TruyenHD/2.2 (com.vnvnads.TruyenHD; build:31; iOS 18.3.1) Alamofire/5.9.0",
    "accept-language": "vi-VN;q=1.0, en-VN;q=0.9",
}

DELAY = 0.02  # 20 ms between attempts
EARLY_MARGIN = 1  # seconds to fire before suggested wait
BURST_SIZE = 5  # number of parallel requests near opening


def sync_server_time():
    """Try to report server clock offset for better timing."""
    try:
        r = requests.head(URL, headers=HEADERS, timeout=5)
        if "Date" in r.headers:
            server_time = parsedate_to_datetime(r.headers["Date"])
            offset = (server_time - datetime.now(timezone.utc)).total_seconds()
            print(f"[i] Server clock ahead by {offset:.3f}s")
        else:
            print("[!] No Date header in server response")
    except Exception as e:
        print(f"[!] Failed to sync time: {e}")


def parse_wait_time(status_text):
    """Parse waiting time from Vietnamese status message.

    Handles both raw Vietnamese text and Unicode-escaped JSON strings.
    Returns wait time in seconds, or None if not found.
    """
    if not status_text:
        return None
    
    # First try to decode Unicode escapes if present
    try:
        # If it's a JSON-like string with Unicode escapes, decode it
        if '\\u' in status_text:
            decoded = status_text.encode('utf-8').decode('unicode_escape')
        else:
            decoded = status_text
    except Exception:
        decoded = status_text

    # Clean the text for parsing
    clean_text = decoded.lower().strip()
    
    # Patterns to match time expressions (ordered by specificity)
    patterns = [
        # Standard Vietnamese
        r"(\d+)\s*giây",
        r"(\d+)\s*phút", 
        r"(\d+)\s*giờ",
        # Unicode escaped versions
        r"(\d+)\s*gi\\u00e2y",  # \u00e2 = â
        r"(\d+)\s*ph\\u00fat",  # \u00fa = ú  
        r"(\d+)\s*gi\\u1edd",  # \u1edd = ờ
        # Corrupted encoding versions
        r"(\d+)\s*(?:giây|phút|giờ|giÃ¢y|phÃºt|giá»)",
        # English fallback
        r"(\d+)\s*(?:second|minute|hour)s?",
        # Just numbers (assume seconds)
        r"(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            matched_text = match.group(0).lower()

            # Determine unit and convert to seconds
            if any(unit in matched_text for unit in ['phút', 'phut', 'ph\\u00fut', 'phÃºt', 'minute']):
                return value * 60
            elif any(unit in matched_text for unit in ['giờ', 'gio', 'gi\\u1edd', 'giá»', 'hour']):
                return value * 3600
            else:  # seconds by default
                return value

    return None


def fire_request(session=None):
    """Send one POST request and return tuple (success, wait_seconds).

    Returns tuple (success, wait_seconds) where wait_seconds is None if
    the response does not specify a waiting time.
    A session can be provided for sequential use. When session is None a
    temporary Session is created so the function is thread safe and can be
    used by workers in a burst.
    """
    close_session = False
    if session is None:
        session = requests.Session()
        session.headers.update(HEADERS)
        close_session = True

    try:
        resp = session.post(URL, json=PAYLOAD, timeout=10)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Pretty print the JSON response for better readability
        try:
            data = resp.json()
            formatted_response = json.dumps(data, ensure_ascii=False, indent=2)
            print(f"{timestamp} POST {resp.status_code}:")
            print(formatted_response)
        except json.JSONDecodeError:
            print(f"{timestamp} POST {resp.status_code}: {resp.text}")
            return False, None

        # Check for success condition
        if data.get("error") == 0:
            return True, None

        # Parse wait time from status message
        status = data.get("status", "")
        wait_seconds = parse_wait_time(status)

        if wait_seconds:
            print(f"[i] Parsed wait time: {wait_seconds} seconds ({wait_seconds // 60}m {wait_seconds % 60}s)")

        return False, wait_seconds

    except requests.exceptions.Timeout:
        print(f"[!] Request timeout")
        return False, None
    except requests.exceptions.ConnectionError:
        print(f"[!] Connection error")
        return False, None
    except Exception as e:
        print(f"[!] Request error: {e}")
        return False, None
    finally:
        if close_session:
            session.close()


def burst_fire(count):
    """Fire multiple requests in parallel and return on first success."""
    print(f"[i] Starting burst of {count} parallel requests...")
    
    wait_hint = None
    with ThreadPoolExecutor(max_workers=count) as ex:
        futures = [ex.submit(fire_request) for _ in range(count)]
        for fut in as_completed(futures):
            try:
                success, wait_seconds = fut.result()
                if success:
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    return True, None
                if wait_hint is None and wait_seconds is not None:
                    wait_hint = wait_seconds
            except Exception as e:
                print(f"[!] Burst request failed: {e}")

    return False, wait_hint


def spam_loop():
    """Repeatedly send requests until success, adapting to wait messages."""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    attempt = 0
    consecutive_failures = 0
    
    try:
        while True:
            attempt += 1
            start = time.time()
            
            print(f"\n[i] Attempt #{attempt}")
            success, wait_seconds = fire_request(session)
            
            if success:
                print("[+] Success! Stopping.")
                break

            consecutive_failures += 1
            
            # If too many consecutive failures, increase delay
            if consecutive_failures > 10:
                print(f"[!] {consecutive_failures} consecutive failures, backing off...")
                time.sleep(5)
                consecutive_failures = 0
            
            if wait_seconds:
                wait = max(wait_seconds - EARLY_MARGIN, 0)
                if wait > 0:
                    print(f"[i] Waiting {wait} seconds before next attempt...")
                    time.sleep(wait)

                # When the window is short, try a burst of parallel requests
                if wait_seconds <= 5:
                    success, hint = burst_fire(BURST_SIZE)
                    if success:
                        print("[+] Success during burst! Stopping.")
                        break
                    if hint:
                        wait_seconds = hint

            # Ensure minimum delay between requests
            elapsed = time.time() - start
            remaining_delay = max(DELAY - elapsed, 0)
            if remaining_delay > 0:
                time.sleep(remaining_delay)
                
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    finally:
        session.close()


if __name__ == "__main__":
    print("[i] Starting API request script...")
    sync_server_time()
    spam_loop()
    print("[i] Script finished.")
