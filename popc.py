import requests as r
import threading as t
import time as tm
import json as j
from colorama import init as i, Fore as F, Style as S

i(autoreset=True)

SUCCESS_COLOR = S.BRIGHT + F.GREEN
ERROR_COLOR = S.BRIGHT + F.RED
WARN_COLOR = S.BRIGHT + F.YELLOW

url = "https://stats.popcat.click/pop?pop_count=800"


def gc(fn):
    with open(fn, "r") as f:
        cd = f.read()

    try:
        c = j.loads(cd)
    except j.JSONDecodeError:
        print("Error parsing cookie data.")
        c = {}
    return c


def sp():
    global pc
    rl = 5
    rc = 0
    s = False

    while not s and rc < rl:
        try:
            ckie = gc("cookies.txt")
            pc = int(ckie["pop_count"])
            sess = r.Session()

            for cn, cv in ckie.items():
                sess.cookies.set(cn, cv)

            resp = sess.post(url)

            if resp.status_code == 201 and len(resp.json()) > 0:
                data = resp.json()
                token = data["Token"]
                url_token = f"{url}?token={token}"
                pc += 800
                sess.cookies.set("pop_count", str(pc))
                updated_cookies = sess.cookies.get_dict()
                cookie_string = "; ".join([f"{k}={v}" for k, v in updated_cookies.items()])
                with open("raw_cookies.txt", "w") as f:
                    f.write(cookie_string)
                with open("cookies.txt", "w") as f:
                    f.write(j.dumps(updated_cookies, indent=4))
                print(f"{SUCCESS_COLOR}Success Popping! Current Pops:", pc)
            else:
                print(f"{ERROR_COLOR}Request failed with status code:", resp.status_code)
            tm.sleep(30)
        except (r.exceptions.RequestException, j.JSONDecodeError, Exception) as e:
            print(f"{ERROR_COLOR}An error occurred:", str(e))
            rc += 1
            print(f"{WARN_COLOR}Retrying... Attempt {rc}/{rl}")
            tm.sleep(1)

    if not s:
        print(f"{ERROR_COLOR}Function failed after {rl} attempts.")


def m():
    t1 = t.Thread(target=sp, daemon=True)
    t1.start()


if __name__ == "__main__":
    m()
