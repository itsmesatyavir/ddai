import requests
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

TOKEN_FILE = 'token.txt'
PROXY_FILE = 'proxy.txt'

colors = {
    "reset": "\033[0m",
    "cyan": "\033[36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "white": "\033[37m",
    "bold": "\033[1m",
}

def log(msg, color="white", symbol=""):
    print(f"{colors[color]}[{symbol}] {msg}{colors['reset']}")

def banner():
    print(f"{colors['cyan']}{colors['bold']}")
    print("---------------------------------------------")
    print("  DDAI Network Bot - FORESTARMY ")
    print("---------------------------------------------" + colors['reset'])

def load_proxies():
    if not os.path.exists(PROXY_FILE):
        log("proxy.txt not found! Please create it with proxy list.", "red", "✗")
        return []
    with open(PROXY_FILE) as f:
        proxies = [line.strip() for line in f if line.strip()]
    log(f"Loaded {len(proxies)} proxies from proxy.txt", "green", "✓")
    return proxies

def format_proxy(proxy):
    return proxy if proxy.startswith("http://") or proxy.startswith("https://") else f"http://{proxy}"

def create_session(proxy=None):
    session = requests.Session()
    if proxy:
        log(f"Using proxy: {proxy}", "white", "➤")
        formatted = format_proxy(proxy)
        session.proxies.update({
            "http": formatted,
            "https": formatted,
        })
    return session

def get_headers(token):
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,id;q=0.8",
        "authorization": f"Bearer {token}",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "Referer": "https://app.ddai.network/"
    }

def read_token():
    return open(TOKEN_FILE).read().strip() if os.path.exists(TOKEN_FILE) else None

def save_token(token):
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)
    log("Token saved to token.txt", "green", "✅")

def login(session):
    log("Attempting to login...", "cyan", "⟳")
    try:
        payload = {"username": USERNAME, "password": PASSWORD}
        headers = get_headers("")
        headers["content-type"] = "application/json"
        res = session.post("https://auth.ddai.network/login", json=payload, headers=headers)
        data = res.json()
        if data.get("status") == "success":
            token = data["data"]["accessToken"]
            log(f"Login successful | Username: {data['data']['user']['username']}", "green", "✅")
            save_token(token)
            return token
        else:
            log(f"Login failed: {data}", "red", "✗")
    except Exception as e:
        log(f"Error during login: {e}", "red", "✗")
    return None

def get_missions(session, token):
    log("Fetching missions...", "cyan", "⟳")
    try:
        res = session.get("https://auth.ddai.network/missions", headers=get_headers(token))
        data = res.json()
        if data.get("status") == "success":
            log(f"Found {len(data['data']['missions'])} missions", "green", "✅")
            return data["data"]["missions"]
        elif res.status_code == 401:
            log("Token expired while fetching missions", "yellow", "⚠")
            return "token_expired"
    except Exception as e:
        log(f"Error fetching missions: {e}", "red", "✗")
    return None

def claim_mission(session, token, mission_id):
    log(f"Claiming mission ID: {mission_id}", "white", "➤")
    try:
        res = session.post(f"https://auth.ddai.network/missions/claim/{mission_id}", headers=get_headers(token))
        data = res.json()
        if data.get("status") == "success":
            log(f"Mission claimed | Reward: {data['data']['rewards']['requests']} requests", "green", "✅")
            return data
        elif res.status_code == 401:
            log("Token expired while claiming mission", "yellow", "⚠")
            return "token_expired"
    except Exception as e:
        log(f"Error claiming mission: {e}", "red", "✗")
    return None

def complete_missions(session, token):
    missions = get_missions(session, token)
    if missions == "token_expired":
        token = login(session)
        if not token:
            return None
        missions = get_missions(session, token)

    if not missions:
        log("Failed to fetch missions, skipping...", "red", "✗")
        return token

    for mission in missions:
        if mission["status"] == "PENDING":
            log(f"Processing mission: {mission['title']}", "white", "➤")
            result = claim_mission(session, token, mission["_id"])
            if result == "token_expired":
                token = login(session)
                if not token:
                    return None
                claim_mission(session, token, mission["_id"])
            time.sleep(2)
        else:
            log(f"Mission already completed: {mission['title']}", "green", "✓")
    log("All missions processed", "green", "✅")
    return token

def model_response(session, token):
    log("Sending Model Response request...", "cyan", "⟳")
    try:
        res = session.get("https://auth.ddai.network/modelResponse", headers=get_headers(token))
        data = res.json()
        log(f"Model Response | Throughput: {data['data']['throughput']}", "green", "✅")
        return data
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            log("Token expired during Model Response", "yellow", "⚠")
            return "token_expired"
    except Exception as e:
        log(f"Error in Model Response: {e}", "red", "✗")
    return None

def onchain_trigger(session, token):
    log("Sending Onchain Trigger request...", "cyan", "⟳")
    try:
        res = session.post("https://auth.ddai.network/onchainTrigger", headers=get_headers(token))
        data = res.json()
        log(f"Onchain Trigger | Requests Total: {colors['yellow']}{data['data']['requestsTotal']}{colors['reset']}", "green", "✅")
        return data
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            log("Token expired during Onchain Trigger", "yellow", "⚠")
            return "token_expired"
    except Exception as e:
        log(f"Error in Onchain Trigger: {e}", "red", "✗")
    return None

def main():
    banner()
    log("Starting DDai Network Auto Bot...", "green", "✓")
    proxies = load_proxies()
    proxy = random.choice(proxies) if proxies else None
    session = create_session(proxy)

    request_count = 0
    token = read_token()
    if not token:
        log("No token found, attempting to login...", "yellow", "⚠")
        token = login(session)
        if not token:
            log("Failed to start bot: Unable to obtain token", "red", "✗")
            return

    log("Starting mission completion process...", "white", "➤")
    token = complete_missions(session, token)
    if not token:
        log("Failed to complete missions, exiting...", "red", "✗")
        return

    log("Starting request loop...", "white", "➤")
    while True:
        try:
            for _ in range(3):
                result = model_response(session, token)
                if result == "token_expired":
                    token = login(session)
                    if not token:
                        raise Exception("Unable to obtain new token")
                    model_response(session, token)

            result = onchain_trigger(session, token)
            if result == "token_expired":
                token = login(session)
                if not token:
                    raise Exception("Unable to obtain new token")
                onchain_trigger(session, token)

            request_count += 1
            log(f"Total Requests Sent: {request_count}", "green", "✓")
            log("Waiting for 30 seconds...", "cyan", "⟳")
            time.sleep(30)

        except Exception as e:
            log(f"Error in main loop: {e}", "red", "✗")
            time.sleep(30)

if __name__ == "__main__":
    main()
