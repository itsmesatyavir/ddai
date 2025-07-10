from aiohttp import ClientSession, ClientError
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, base64, time, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class DDAI:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://app.ddai.space",
            "Referer": "https://app.ddai.space/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://auth.ddai.space"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.refresh_tokens = {}
        self.session = None

    async def create_session(self):
        self.session = ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}DDAI Network - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT} https://youtube.com/forestarmy {Fore.YELLOW + Style.BRIGHT} https://t.me/forestarmy 
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "tokens.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return []

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []

    def save_tokens(self, new_accounts):
        filename = "tokens.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["Email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["Email"]] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

        except Exception as e:
            return []

    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with self.session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open(filename, 'w') as f:
                        f.write(content)
                    self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, user_id):
        if user_id not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[user_id] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[user_id]

    def rotate_proxy_for_account(self, user_id):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[user_id] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def get_token_exp_time(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            exp_time = parsed_payload["exp"]
            return exp_time
        except Exception as e:
            return None
            
    def biner_to_desimal(self, troughput: str):
        desimal = int(troughput, 2)
        return desimal
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
    
    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip().lower()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate

    async def onchain_trigger(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/onchainTrigger"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[user_id]}",
            "Content-Length": "0",
            "Origin": "chrome-extension://pigpomlidebemiifjihbgicepgbamdaj",
            "Sec-Fetch-Storage-Access": "active",
        }
        
        for attempt in range(retries):
            try:
                async with self.session.post(
                    url=url,
                    headers=headers,
                    proxy=proxy,
                    timeout=60,
                    ssl=False
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except ClientError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(user_id, proxy, Fore.YELLOW, f"Onchain Trigger Failed: {Fore.RED+Style.BRIGHT}{str(e)}")

        return None

    async def auth_refresh(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/refresh"
        data = json.dumps({"refreshToken": self.refresh_tokens[email]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            try:
                async with self.session.post(
                    url=url,
                    headers=headers,
                    data=data,
                    proxy=proxy,
                    timeout=60,
                    ssl=False
                ) as response:
                    if response.status == 401:
                        self.print_message(email, proxy, Fore.RED, "Refreshing Access Token Failed: "
                            f"{Fore.YELLOW + Style.BRIGHT}Already Expired{Style.RESET_ALL}"
                        )
                        return None
                    elif response.status == 403:
                        self.print_message(email, proxy, Fore.RED, "Refreshing Access Token Failed: "
                            f"{Fore.YELLOW + Style.BRIGHT}Invalid, PLEASE DON'T LOGOUT or OPENED DDAI DASHBOARD WHILE BOT RUNNING{Style.RESET_ALL}"
                        )
                        return None
                    response.raise_for_status()
                    return await response.json()
            except ClientError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.YELLOW, f"Refreshing Access Token Failed: {Fore.RED+Style.BRIGHT}{str(e)}")

        return None
            
    async def model_response(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/modelResponse"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        
        for attempt in range(retries):
            try:
                async with self.session.get(
                    url=url,
                    headers=headers,
                    proxy=proxy,
                    timeout=60,
                    ssl=False
                ) as response:
                    if response.status == 401:
                        await self.process_auth_refresh(email, use_proxy, rotate_proxy)
                        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                        continue
                    response.raise_for_status()
                    return await response.json()
            except ClientError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.YELLOW, f"GET Troughput Data Failed: {Fore.RED+Style.BRIGHT}{str(e)}")

        return None
    
    async def mission_lists(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/missions"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        
        for attempt in range(retries):
            try:
                async with self.session.get(
                    url=url,
                    headers=headers,
                    proxy=proxy,
                    timeout=60,
                    ssl=False
                ) as response:
                    if response.status == 401:
                        await self.process_auth_refresh(email, use_proxy, rotate_proxy)
                        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                        continue
                    response.raise_for_status()
                    return await response.json()
            except ClientError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.YELLOW, f"GET Mission Lists Failed: {Fore.RED+Style.BRIGHT}{str(e)}")

        return None
    
    async def complete_missions(self, email: str, mission_id: str, title: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/missions/claim/{mission_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Content-Length": "0"
        }
        
        for attempt in range(retries):
            try:
                async with self.session.post(
                    url=url,
                    headers=headers,
                    proxy=proxy,
                    timeout=60,
                    ssl=False
                ) as response:
                    if response.status == 401:
                        await self.process_auth_refresh(email, use_proxy, rotate_proxy)
                        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                        continue
                    response.raise_for_status()
                    return await response.json()
            except ClientError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                    f"{Fore.RED + Style.BRIGHT} Not Completed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None

    async def process_auth_refresh(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            refresh = await self.auth_refresh(email, proxy)
            if refresh:
                self.access_tokens[email] = refresh["data"]["accessToken"]
                self.save_tokens([{"Email": email, "accessToken": self.access_tokens[email], "refreshToken": self.refresh_tokens[email]}])
                self.print_message(email, proxy, Fore.GREEN, "Refreshing Access Token Success")
                return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(email)

            await asyncio.sleep(5)
            continue
        
    async def check_token_exp_time(self, email: str, use_proxy: bool, rotate_proxy: bool):
        exp_time = self.get_token_exp_time(self.access_tokens[email])

        if int(time.time()) > exp_time:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            self.print_message(email, proxy, Fore.YELLOW, "Access Token Expired, Refreshing...")
            await self.process_auth_refresh(email, use_proxy, rotate_proxy)

        return True

    async def looping_auth_refresh(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            await asyncio.sleep(10 * 60)
            await self.process_auth_refresh(email, use_proxy, rotate_proxy)

    async def process_onchain_trigger(self, email: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.check_token_exp_time(email, use_proxy, rotate_proxy)
        if is_valid:
            while True:
                proxy = self.get_next_proxy_for_account(email) if use_proxy else None

                model = await self.onchain_trigger(email, proxy)
                if model:
                    req_total = model.get("data", {}).get("requestsTotal", 0)
                    self.print_message(email, proxy, Fore.GREEN, "Onchain Triggered Successfully "
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Total Requests: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{req_total}{Style.RESET_ALL}"
                    )
                    return True
                
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(email)

                await asyncio.sleep(5)
                continue
        
    async def process_model_response(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            model = await self.model_response(email, use_proxy, rotate_proxy, proxy)
            if model:
                throughput = model.get("data", {}).get("throughput", 0)
                formatted_throughput = self.biner_to_desimal(throughput)
                self.print_message(email, proxy, Fore.GREEN, "Throughput "
                    f"{Fore.WHITE + Style.BRIGHT}{formatted_throughput}%{Style.RESET_ALL}"
                )

            await asyncio.sleep(60)

    async def process_user_missions(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            mission_lists = await self.mission_lists(email, use_proxy, rotate_proxy, proxy)
            if mission_lists:
                missions = mission_lists.get("data", {}).get("missions", [])

                if missions:
                    completed = False

                    for mission in missions:
                        if mission:
                            mission_id = mission.get("_id")
                            title = mission.get("title")
                            reward = mission.get("rewards", {}).get("requests", 0)
                            type = mission.get("type")
                            status = mission.get("status")

                            if type == 3:
                                if status == "COMPLETED":
                                    claim = await self.complete_missions(email, mission_id, title, use_proxy, rotate_proxy, proxy)
                                    if claim and claim.get("data", {}).get("claimed"):
                                        self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{reward} Requests{Style.RESET_ALL}"
                                        )
                            
                            else:
                                if status == "PENDING":
                                    claim = await self.complete_missions(email, mission_id, title, use_proxy, rotate_proxy, proxy)
                                    if claim and claim.get("data", {}).get("claimed"):
                                        self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{reward} Requests{Style.RESET_ALL}"
                                        )
                        else:
                            completed = True

                    if completed:
                        self.print_message(email, proxy, Fore.GREEN, "All Available Mission Is Completed")

            await asyncio.sleep(24 * 60 * 60)
        
    async def process_accounts(self, email: str, use_proxy: bool, rotate_proxy: bool):
        triggered = await self.process_onchain_trigger(email, use_proxy, rotate_proxy)
        if triggered:
            tasks = [
                asyncio.create_task(self.looping_auth_refresh(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.process_model_response(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.process_user_missions(email, use_proxy, rotate_proxy))
            ]
            await asyncio.gather(*tasks)
    
    async def main(self):
        try:
            await self.create_session()
            tokens = self.load_accounts()
            if not tokens:
                self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            use_proxy_choice, rotate_proxy = self.print_question()
            use_proxy = use_proxy_choice in [1, 2]

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*75)

            tasks = []
            for idx, token in enumerate(tokens, start=1):
                if token:
                    email = token["Email"]
                    access_token = token["accessToken"]
                    refresh_token = token["refreshToken"]

                    if not "@" in email or not access_token or not refresh_token:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    exp_time = self.get_token_exp_time(refresh_token)
                    if int(time.time()) > exp_time:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Refresh Token Already Expired {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    self.access_tokens[email] = access_token
                    self.refresh_tokens[email] = refresh_token

                    tasks.append(asyncio.create_task(self.process_accounts(email, use_proxy, rotate_proxy)))

            await asyncio.gather(*tasks)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e
        finally:
            await self.close_session()

if __name__ == "__main__":
    try:
        bot = DDAI()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] DDAI Network - BOT{Style.RESET_ALL}"
        )
