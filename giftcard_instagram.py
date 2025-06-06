import json
import os
import time
from typing import Dict, List
from urllib import request, parse

HASHTAG = "OurStore"  # without the '#'
REWARD_LEVELS = {
    1: "free fries",
    2: "free coke",
    3: "free hamburger"
}

USER_DATA_FILE = "user_counts.json"
LAST_TIMESTAMP_FILE = "last_timestamp.txt"

IG_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
IG_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
GIFT_CARD_ENDPOINT = os.getenv("GIFT_CARD_ENDPOINT")
GIFT_CARD_API_KEY = os.getenv("GIFT_CARD_API_KEY")

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
    if not (GIFT_CARD_ENDPOINT and GIFT_CARD_API_KEY):
        # Fallback to console output if no provider configured
        print(f"Would send '{reward}' to {user}")
        return

    data = json.dumps({"recipient": user, "reward": reward}).encode()
    req = request.Request(
        GIFT_CARD_ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GIFT_CARD_API_KEY}",
        },
    )
    with request.urlopen(req) as resp:
        print(f"Gift card sent to {user}, response status {resp.status}")


def process_post(user: str, hashtag: str, counts: Dict[str, int]):
    if hashtag != HASHTAG:
        return
    count = counts.get(user, 0) + 1
    reward = REWARD_LEVELS.get(count)
    if reward:
        send_gift_card(user, reward)
    counts[user] = count

def fetch_hashtag_id() -> str:
    if not (IG_BUSINESS_ID and IG_ACCESS_TOKEN):
        raise EnvironmentError("Instagram credentials not configured")
    query = parse.urlencode(
        {
            "user_id": IG_BUSINESS_ID,
            "q": HASHTAG,
            "access_token": IG_ACCESS_TOKEN,
        }
    )
    url = f"https://graph.facebook.com/v19.0/ig_hashtag_search?{query}"
    with request.urlopen(url) as resp:
        data = json.load(resp)
    return data["data"][0]["id"]


def fetch_recent_posts(hashtag_id: str, since_ts: int) -> List[Dict]:
    query = parse.urlencode(
        {
            "user_id": IG_BUSINESS_ID,
            "fields": "id,username,timestamp",
            "since": since_ts,
            "access_token": IG_ACCESS_TOKEN,
        }
    )
    url = f"https://graph.facebook.com/v19.0/{hashtag_id}/recent_media?{query}"
    with request.urlopen(url) as resp:
        return json.load(resp).get("data", [])


def main():
    counts = load_user_counts()
    last_ts = load_last_timestamp()

    hashtag_id = fetch_hashtag_id()
    posts = fetch_recent_posts(hashtag_id, last_ts)

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
