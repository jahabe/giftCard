# Gift Card Automation

This repository contains a script that can automatically reward customers who use a store hashtag on Instagram. It keeps track of how many times each user has posted and sends different gifts in response.

Rewards:
1. First post: free fries
2. Second post: free coke
3. Third post: free hamburger

`giftcard_instagram.py` now integrates with the Instagram Graph API and can call an HTTP gift-card provider. User counts are stored in `user_counts.json`.

To run this script against real data you must supply API credentials via environment variables:

```bash
export INSTAGRAM_BUSINESS_ID=<your_business_id>
export INSTAGRAM_ACCESS_TOKEN=<your_access_token>
export GIFT_CARD_ENDPOINT=https://your.giftcard.provider/send
export GIFT_CARD_API_KEY=<provider_api_key>
```

## Running the example

Run the script with Python 3:

```bash
python3 giftcard_instagram.py
```

The script processes posts containing the hashtag and sends gifts as users meet each reward threshold.
