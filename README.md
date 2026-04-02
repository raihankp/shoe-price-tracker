# 🛍️ Melissa Price Tracker

Monitors the price of a Melissa shoe product and sends you a notification
(via **Ntfy** or **Telegram**) when the price drops to your target.

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

## Option B: Ntfy.sh Setup (Recommended — Simplest)

### Step 1 — Install Ntfy on your phone
- Android: [Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
- iOS: [App Store](https://apps.apple.com/app/ntfy/id1625396347)

### Step 2 — Subscribe to your topic
1. Open Ntfy app
2. Tap **+** → **Subscribe to topic**
3. Enter your topic name (same as `NTFY_TOPIC` in tracker.py)
   → Example: `melissa-price-tracker-yourname`
4. Use server: `https://ntfy.sh` (default)

> ⚠️ Pick a unique topic name — ntfy topics are public!
> Anyone who knows your topic name can subscribe.
> Use something random like `melissa-sophie-xk7r2q`

### Step 3 — Edit tracker.py
```python
NTFY_TOPIC  = "melissa-sophie-xk7r2q"   # your unique topic
TARGET_PRICE = 500_000                   # your target in IDR
NTFY_ENABLED = True
TELEGRAM_ENABLED = False
```

---

## Option C: Telegram Bot Setup

### Step 1 — Create a bot
1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts → you'll get a **Bot Token** like:
   `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2 — Get your Chat ID
1. Search for **@userinfobot** on Telegram
2. Send `/start` → it replies with your **Chat ID** (a number like `123456789`)

### Step 3 — Edit tracker.py
```python
TELEGRAM_ENABLED    = True
TELEGRAM_BOT_TOKEN  = "7123456789:AAFxxxxx..."
TELEGRAM_CHAT_ID    = "123456789"
NTFY_ENABLED        = False     # or keep True to use both!
```

---

## Deploy to Render.com (Free)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "melissa tracker"
git remote add origin https://github.com/YOUR_USERNAME/melissa-tracker.git
git push -u origin main
```

### Step 2 — Create a Render account
Go to [render.com](https://render.com) and sign up (free)

### Step 3 — New Background Worker
1. Dashboard → **New +** → **Background Worker**
2. Connect your GitHub repo
3. Render auto-detects `render.yaml` — click **Create**
4. Done! Your tracker is live 24/7 🎉

### Checking logs
- Go to Render dashboard → your service → **Logs**
- You'll see something like:
  ```
  [2026-04-02 09:00:01] Checking price...
    💰 Current price: IDR 900.000
    🎯 Target price:  IDR 500.000
    ⏳ Not there yet. Sending hourly update...
    💤 Sleeping 60 minutes...
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
