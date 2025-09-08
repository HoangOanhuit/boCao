import time
import requests
from datetime import datetime
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
    "registered": "2025-02-14 07:24:34"  # FIXED: dùng timestamp cố định
}     # Adjust per API
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
        offset = (server_time - datetime.utcnow()).total_seconds()
        print(f"[i] Server clock ahead by {offset:.3f}s")
    except Exception as e:
        print(f"[!] Failed to sync time: {e}")


def fire_request(session):
    """Send one POST request using persistent session."""
    try:
        resp = session.post(URL, data=PAYLOAD, timeout=5)
        print(f"{time.strftime('%H:%M:%S.%f')[:-3]} POST {resp.status_code}: {resp.text}")
        return '"error":0' in resp.text
    except Exception as e:
        print(f"[!] Request error: {e}")
        return False


def spam_loop():
    """Repeatedly send requests every DELAY seconds until success."""
    session = requests.Session()
    session.headers.update(HEADERS)
    while True:
        start = time.time()
        if fire_request(session):
            print("[+] Success! Stopping.")
            break
        elapsed = time.time() - start
        time.sleep(max(DELAY - elapsed, 0))


if __name__ == "__main__":
    sync_server_time()
    spam_loop()
