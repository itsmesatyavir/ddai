# DDai Network Auto Bot

Automated bot for DDai Network to complete missions, claim rewards, and send requests.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/itsmesatyavir/ddai
cd ddai
```

2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Configure environment variables

Create a .env file in the root directory:
```
nano .env
```
Add your DDai account credentials:
```bash
USERNAME=your_ddai_username
PASSWORD=your_ddai_password
```
Save and exit.

4. (Optional) Configure proxies

Create a proxy.txt file in the root directory to use proxies:
```bash
nano proxy.txt
```
Add proxies line by line in one of these formats:

```
ip:port
username:password@ip:port

Example:

123.45.67.89:8080
user:pass@123.45.67.89:8080
```
Save and exit.

5. Run the bot

```bash
python main.py
```

---

Notes

The bot will automatically login using the credentials in .env.

If proxy.txt exists, it will randomly use one proxy for requests.

Logs and status messages will appear in the terminal.



---

Troubleshooting

Ensure .env file is correctly formatted.

Make sure dependencies are installed.

Check proxy format if you experience connection issues.



---

License

MIT License



