# Gift Card Automation

This repository contains a simple script that demonstrates how to reward customers who use a store hashtag on Instagram. The script tracks each user's posts and sends different rewards depending on how many times they have posted with the hashtag.

Rewards:
1. First post: free fries
2. Second post: free coke
3. Third post: free hamburger

The script `giftcard_instagram.py` is a standalone example and uses a local JSON file to remember user counts. In a production environment, you would replace the placeholder Instagram data and gift card delivery logic with real implementations.

## Running the example

Run the script with Python 3:

```bash
python3 giftcard_instagram.py
```

This will simulate processing a few posts and print the gifts that would be sent.
