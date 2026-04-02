# 🛍️ Shoe Price Tracker

Monitors the price of a Melissa shoe product and sends you a notification
(via **Ntfy**) when the price drops to your target.

---

## Files

```
melissa-tracker/
├── tracker.py        ← main script
├── requirements.txt  ← dependencies
├── render.yaml       ← deploy config for Render.com
└── README.md         ← this file
```

---

## Ntfy.sh Setup

### Step 1 — Install Ntfy on your phone
- Android: [Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
- iOS: [App Store](https://apps.apple.com/app/ntfy/id1625396347)

### Step 2 — Subscribe to your topic
1. Open Ntfy app
2. Tap **+** → **Subscribe to topic**
3. Enter your topic name (same as `NTFY_TOPIC` in tracker.py)
   → Example: `melissa-price-tracker-kape`
4. Use server: `https://ntfy.sh` (default)

> ⚠️ Pick a unique topic name — ntfy topics are public!
> Anyone who knows your topic name can subscribe.

### Step 3 — Edit tracker.py
```python
NTFY_TOPIC  = "melissa-price-tracker-kape"   # your unique topic
TARGET_PRICE = 500_000                   # your target in IDR
NTFY_ENABLED = True
```

---

## Running locally (for testing)

```bash
pip install -r requirements.txt
python tracker.py
```

---

## Configuration reference

| Variable | Default | Description |
|---|---|---|
| `TARGET_PRICE` | 500000 | Alert when price ≤ this (IDR) |
| `CHECK_INTERVAL` | 3600 | Seconds between checks (3600 = 1 hour) |
| `NTFY_TOPIC` | `melissa-price-tracker-yourname` | Your unique ntfy topic |
| `SEND_HOURLY_UPDATES` | True | Send update every hour even if not on target |
| `NTFY_ENABLED` | True | Enable ntfy notifications |
| `TELEGRAM_ENABLED` | False | Enable Telegram notifications |

You can enable **both** Ntfy and Telegram at the same time!
