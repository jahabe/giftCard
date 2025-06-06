import json
from typing import Dict

HASHTAG = "#OurStore"
REWARD_LEVELS = {
    1: "free fries",
    2: "free coke",
    3: "free hamburger"
}

USER_DATA_FILE = "user_counts.json"

def load_user_counts() -> Dict[str, int]:
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_counts(counts: Dict[str, int]):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(counts, f)


def send_gift_card(user: str, reward: str):
    """Placeholder for gift card sending logic."""
    print(f"Sent to {user}: {reward}")


def process_post(user: str, hashtag: str, counts: Dict[str, int]):
    if hashtag != HASHTAG:
        return
    count = counts.get(user, 0) + 1
    reward = REWARD_LEVELS.get(count)
    if reward:
        send_gift_card(user, reward)
    counts[user] = count


def main():
    # Placeholder for fetching posts from Instagram.
    # Simulated posts list of (user, hashtag) pairs.
    posts = [
        ("alice", "#OurStore"),
        ("bob", "#OurStore"),
        ("alice", "#OurStore"),
        ("alice", "#OurStore"),
    ]

    counts = load_user_counts()
    for user, tag in posts:
        process_post(user, tag, counts)
    save_user_counts(counts)


if __name__ == "__main__":
    main()
