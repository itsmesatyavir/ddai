import requests
import time
import random
import os
from datetime import datetime

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
    print("  DDAI SPACE BOT - FORESTARMY ")
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
        "authorization": f"Bearer {token}",
        "Referer": "https://app.ddai.space/"
    }

def read_token():
    if os.path.exists(TOKEN_FILE):
        return open(TOKEN_FILE).read().strip()
    else:
        log("token.txt not found! Please create it with your token.", "red", "✗")
        return None

def get_missions(session, token):
    log("Fetching missions...", "cyan", "⟳")
    try:
        res = session.get("https://auth.ddai.space/missions", headers=get_headers(token))
        if res.status_code == 401:
            log("Token expired or invalid while fetching missions", "yellow", "⚠")
            return "token_expired"
        data = res.json()
        missions = data.get("data", {}).get("missions", [])
        log(f"Found {len(missions)} missions", "green", "✓")
        return missions
    except Exception as e:
        log(f"Error fetching missions: {e}", "red", "✗")
        return None

def claim_mission(session, token, mission_id):
    log(f"Claiming mission ID: {mission_id}", "white", "➤")
    try:
        res = session.post(f"https://auth.ddai.space/missions/claim/{mission_id}", headers=get_headers(token))
        if res.status_code == 401:
            log("Token expired while claiming mission", "yellow", "⚠")
            return "token_expired"
        data = res.json()
        if data.get("status") == "success":
            reward = data["data"]["rewards"]["requests"]
            log(f"Mission claimed | Reward: {reward} requests", "green", "✅")
            return data
    except Exception as e:
        log(f"Error claiming mission: {e}", "red", "✗")
    return None

def complete_missions(session, token):
    missions = get_missions(session, token)
    if missions == "token_expired":
        log("Token is invalid or expired. Cannot continue.", "red", "✗")
        return None
    if not missions:
        log("No missions found or fetch failed", "red", "✗")
        return token

    for mission in missions:
        if mission["status"] == "PENDING":
            log(f"Processing mission: {mission['title']}", "white", "➤")
            result = claim_mission(session, token, mission["_id"])
            if result == "token_expired":
                log("Token expired during mission claiming. Stopping.", "red", "✗")
                return None
            time.sleep(2)
        else:
            log(f"Already completed: {mission['title']}", "yellow", "✓")
    log("All available missions processed", "green", "✅")
    return token

def model_response(session, token):
    log("Sending Model Response request...", "cyan", "⟳")
    try:
        res = session.get("https://auth.ddai.space/modelResponse", headers=get_headers(token))
        if res.status_code == 401:
            log("Token expired during Model Response", "yellow", "⚠")
            return "token_expired"
        data = res.json()
        throughput = data.get("data", {}).get("throughput", "0")
        decimal = int(throughput, 2)
        log(f"Model Response | Throughput: {throughput} (Decimal: {decimal})", "green", "✅")
        return data
    except Exception as e:
        log(f"Error in Model Response: {e}", "red", "✗")
    return None

def onchain_trigger(session, token):
    log("Sending Onchain Trigger request...", "cyan", "⟳")
    try:
        res = session.post("https://auth.ddai.space/onchainTrigger", headers=get_headers(token))
        if res.status_code == 401:
            log("Token expired during Onchain Trigger", "yellow", "⚠")
            return "token_expired"
        data = res.json()
        total = data.get("data", {}).get("requestsTotal", "N/A")
        log(f"Onchain Trigger | Requests Total: {colors['yellow']}{total}{colors['reset']}", "green", "✅")
        return data
    except Exception as e:
        log(f"Error in Onchain Trigger: {e}", "red", "✗")
    return None

def main():
    banner()
    log("Starting DDai SPACE Bot...", "green", "✓")
    proxies = load_proxies()
    proxy = random.choice(proxies) if proxies else None
    session = create_session(proxy)

    token = read_token()
    if not token:
        log("No token found, exiting...", "red", "✗")
        return

    # Complete missions once at the beginning
    token = complete_missions(session, token)
    if not token:
        log("Missions could not be completed. Exiting.", "red", "✗")
        return

    request_count = 0
    while True:
        try:
            for _ in range(3):
                result = model_response(session, token)
                if result == "token_expired":
                    log("Token expired. Exiting.", "red", "✗")
                    return

            result = onchain_trigger(session, token)
            if result == "token_expired":
                log("Token expired. Exiting.", "red", "✗")
                return

            request_count += 1
            log(f"Total Requests Sent: {request_count}", "green", "✓")
            delay = random.randint(10, 60)
            log(f"Waiting for {delay} seconds...", "cyan", "⏳")
            time.sleep(delay)

        except Exception as e:
            log(f"Error in main loop: {e}", "red", "✗")
            time.sleep(30)

if __name__ == "__main__":
    main()
