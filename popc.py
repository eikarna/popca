import sys
import requests
import threading
import time
import json
from colorama import init, Fore, Style

init(autoreset=True)

SUCCESS_COLOR = Style.BRIGHT + Fore.GREEN
ERROR_COLOR = Style.BRIGHT + Fore.RED
WARN_COLOR = Style.BRIGHT + Fore.YELLOW

url = "https://stats.popcat.click/pop?pop_count=800"


def get_cookie(file_name):
    # Read the cookie data from the file
    with open(file_name, "r") as file:
        cookie_data = file.read()

    try:
        # Parse the cookie data into a dictionary
        cookies = json.loads(cookie_data)
    except json.JSONDecodeError:
        print("Error parsing cookie data.")
        cookies = {}
    return cookies


def spam(cookie_file):
    global pop_count
    retry_limit = 5
    retry_count = 0
    success = False

    while not success and retry_count < retry_limit:
        try:
            # Get the cookies from the provided file
            cookies = get_cookie(cookie_file)
            pop_count = int(cookies["pop_count"])
            session = requests.Session()

            # Set the cookies in the session
            for cookie_name, cookie_value in cookies.items():
                session.cookies.set(cookie_name, cookie_value)

            # Send the POST request to pop the cat
            response = session.post(url)

            if response.status_code == 201 and len(response.json()) > 0:
                # If the request was successful, update the pop count
                data = response.json()
                token = data["Token"]
                url_with_token = f"{url}?token={token}"
                pop_count += 800
                session.cookies.set("pop_count", str(pop_count))
                updated_cookies = session.cookies.get_dict()

                # Save the updated cookies to files
                cookie_string = "; ".join([f"{key}={value}" for key, value in updated_cookies.items()])
                with open("raw_cookies.txt", "w") as file:
                    file.write(cookie_string)
                with open("cookies.txt", "w") as file:
                    file.write(json.dumps(updated_cookies, indent=4))

                # Print the success message
                print(f"{SUCCESS_COLOR}Success Popping! Current Pops:", pop_count)
            else:
                # Print error message if the request failed
                print(f"{ERROR_COLOR}Request failed with status code:", response.status_code)

            # Wait for 30 seconds before the next request
            time.sleep(30)
        except (requests.exceptions.RequestException, json.JSONDecodeError, Exception) as e:
            # Handle exceptions and retry if necessary
            print(f"{ERROR_COLOR}An error occurred:", str(e))
            retry_count += 1
            print(f"{WARN_COLOR}Retrying... Attempt {retry_count}/{retry_limit}")
            time.sleep(1)

    if not success:
        print(f"{ERROR_COLOR}Function failed after {retry_limit} attempts.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py [cookie_file]")
        return

    # Get the cookie file name from command-line argument
    cookie_file = sys.argv[1]
    spam(cookie_file)


if __name__ == "__main__":
    main()
