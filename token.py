import json

def main():
    data = []

    try:
        count = int(input("How many accounts do you want to save? "))
    except ValueError:
        print("Please enter a valid number.")
        return

    for i in range(count):
        print(f"\n--- Account {i + 1} ---")
        email = input("Enter Email: ").strip()
        access_token = input("Enter Access Token: ").strip()
        refresh_token = input("Enter Refresh Token: ").strip()

        account = {
            "Email": email,
            "accessToken": access_token,
            "refreshToken": refresh_token
        }

        data.append(account)

    # Save to JSON file
    with open("tokens.json", "w") as f:
        json.dump(data, f, indent=2)

    print("\n✅ All data saved to 'tokens.json'!")

if __name__ == "__main__":
    main()
