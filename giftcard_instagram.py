import json
import os
import re
import ssl
import time
from typing import Dict, List
from urllib import request, parse
from urllib.error import HTTPError, URLError

HASHTAG = "OurStore"  # without the '#'
REWARD_LEVELS = {
    1: "free fries",
    2: "free coke",
    3: "free hamburger"
}

USER_DATA_FILE = "user_counts.json"
LAST_TIMESTAMP_FILE = "last_timestamp.txt"

REQUEST_TIMEOUT = 10
SSL_CONTEXT = ssl.create_default_context()
def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable {name}")
    return value


def get_dm_endpoint() -> str:
    business_id = require_env("INSTAGRAM_BUSINESS_ID")
    return f"https://graph.facebook.com/v19.0/{business_id}/messages"

def load_user_counts() -> Dict[str, int]:
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_counts(counts: Dict[str, int]):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(counts, f)

def load_last_timestamp() -> int:
    try:
        with open(LAST_TIMESTAMP_FILE, "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return 0


def save_last_timestamp(ts: int):
    with open(LAST_TIMESTAMP_FILE, "w") as f:
        f.write(str(ts))


def send_gift_card(user: str, reward: str):
    """Send a gift card using an HTTP API."""
    endpoint = os.getenv("GIFT_CARD_ENDPOINT")
    api_key = os.getenv("GIFT_CARD_API_KEY")
    if not (endpoint and api_key):
        print(f"Would send '{reward}' to {user}")
        return

    data = json.dumps({"recipient": user, "reward": reward}).encode()
    req = request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT, context=SSL_CONTEXT) as resp:
            print(f"Gift card sent to {user}, response status {resp.status}")
    except (HTTPError, URLError) as e:
        print(f"Failed to send gift card to {user}: {e}")


def send_direct_message(username: str, text: str):
    """Send a direct message via the Instagram Graph API."""
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not token:
        print(f"Would DM {username}: {text}")
        return
    if not re.fullmatch(r"[A-Za-z0-9._]{1,30}", username):
        print(f"Invalid username {username!r}")
        return

    data = parse.urlencode(
        {
            "messaging_product": "instagram",
            "recipient": json.dumps({"username": username}),
            "message": json.dumps({"text": text}),
            "access_token": token,
        }
    ).encode()
    endpoint = get_dm_endpoint()
    req = request.Request(endpoint, data=data)
    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT, context=SSL_CONTEXT) as resp:
            print(f"DM sent to {username}, response status {resp.status}")
    except (HTTPError, URLError) as e:
        print(f"Failed to DM {username}: {e}")


def process_post(user: str, hashtag: str, counts: Dict[str, int]):
    if hashtag != HASHTAG:
        return
    count = counts.get(user, 0) + 1
    reward = REWARD_LEVELS.get(count)
    if reward:
        send_gift_card(user, reward)
        send_direct_message(user, f"Here is your reward: {reward}")
    counts[user] = count

def fetch_hashtag_id() -> str:
    business_id = require_env("INSTAGRAM_BUSINESS_ID")
    token = require_env("INSTAGRAM_ACCESS_TOKEN")
    query = parse.urlencode(
        {
            "user_id": business_id,
            "q": HASHTAG,
            "access_token": token,
        }
    )
    url = f"https://graph.facebook.com/v19.0/ig_hashtag_search?{query}"
    try:
        with request.urlopen(url, timeout=REQUEST_TIMEOUT, context=SSL_CONTEXT) as resp:
            data = json.load(resp)
        return data["data"][0]["id"]
    except (HTTPError, URLError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to fetch hashtag id: {e}")


def fetch_recent_posts(hashtag_id: str, since_ts: int) -> List[Dict]:
    query = parse.urlencode(
        {
            "user_id": require_env("INSTAGRAM_BUSINESS_ID"),
            "fields": "id,username,timestamp",
            "since": since_ts,
            "access_token": require_env("INSTAGRAM_ACCESS_TOKEN"),
        }
    )
    url = f"https://graph.facebook.com/v19.0/{hashtag_id}/recent_media?{query}"
    try:
        with request.urlopen(url, timeout=REQUEST_TIMEOUT, context=SSL_CONTEXT) as resp:
            return json.load(resp).get("data", [])
    except (HTTPError, URLError, json.JSONDecodeError) as e:
        print(f"Failed to fetch posts: {e}")
        return []


def main():
    counts = load_user_counts()
    last_ts = load_last_timestamp()

    try:
        hashtag_id = fetch_hashtag_id()
        posts = fetch_recent_posts(hashtag_id, last_ts)
    except RuntimeError as e:
        print(e)
        return

    for post in posts:
        user = post["username"]
        ts_struct = time.strptime(post["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
        ts = int(time.mktime(ts_struct))
        process_post(user, HASHTAG, counts)
        last_ts = max(last_ts, ts)

    save_user_counts(counts)
    save_last_timestamp(last_ts)


if __name__ == "__main__":
    main()
