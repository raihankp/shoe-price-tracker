import requests
import re
import time
from datetime import datetime

# ─────────────────────────────────────────
#  CONFIG — edit these values
# ─────────────────────────────────────────
PRODUCT_URL    = "https://melissa.co.id/products/melissa-sophie-ad-pearly-black"
PRODUCT_NAME   = "Melissa Sophie AD - Pearly Black"
TARGET_PRICE   = 500_000          # notify if price <= this (IDR)
CHECK_INTERVAL = 60             # seconds between checks (3600 = 1 hour)

# --- Option B: Ntfy.sh ---
NTFY_ENABLED   = True
NTFY_TOPIC     = "melissa-price-tracker-kape"   # change to something unique!
NTFY_SERVER    = "https://ntfy.sh"

# --- Option C: Telegram ---
TELEGRAM_ENABLED    = False
TELEGRAM_BOT_TOKEN  = "YOUR_BOT_TOKEN_HERE"         # from @BotFather
TELEGRAM_CHAT_ID    = "YOUR_CHAT_ID_HERE"            # from @userinfobot
# ─────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_price() -> int | None:
    """
    Scrape the current sale price from the product page.

    DOM path we follow (from the actual page HTML):
        <article class="product" ...>
            <div class="product-meta">
                <div class="product-price sale">
                    IDR 900.000          <- we want THIS
                    <span class="down-from-price">IDR 1.000.000</span>  <- NOT this
                    <span class="sale-percentage">-10%</span>            <- NOT this
                </div>

    We drill down step by step so we never accidentally grab a price
    from a different section of the page.
    """
    try:
        resp = requests.get(PRODUCT_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # Step 1: Isolate <article class="product">
        # There may be other price elements outside this article (e.g. recently
        # viewed, recommended products). This pins us to the main product only.
        article_match = re.search(
            r'<article[^>]+class="[^"]*\bproduct\b[^"]*"[^>]*>(.*?)</article>',
            html,
            re.DOTALL | re.IGNORECASE
        )
        if not article_match:
            print("  ⚠️  Could not find <article class='product'>.")
            return None
        article = article_match.group(1)

        # Step 2: Narrow to <div class="product-meta">
        # This div wraps the title, price, and form — excludes image carousel etc.
        meta_match = re.search(
            r'<div[^>]+class="[^"]*\bproduct-meta\b[^"]*"[^>]*>(.*)',
            article,
            re.DOTALL | re.IGNORECASE
        )
        scope = meta_match.group(1) if meta_match else article

        # Step 3: Extract <div class="product-price ...">
        # The actual class value has newlines ("product-price\n  sale\n") so
        # we match loosely with \bproduct-price\b.
        block_match = re.search(
            r'<div[^>]+class="[^"]*\bproduct-price\b[^"]*"[^>]*>(.*?)</div>',
            scope,
            re.DOTALL | re.IGNORECASE
        )
        if not block_match:
            print("  ⚠️  Could not find div.product-price.")
            return None
        block = block_match.group(1)

        # Step 4: Strip child spans we don't want
        # Remove <span class="down-from-price"> (original/strikethrough price)
        block = re.sub(
            r'<span[^>]+class="[^"]*\bdown-from-price\b[^"]*"[^>]*>.*?</span>',
            '', block, flags=re.DOTALL | re.IGNORECASE
        )
        # Remove <span class="sale-percentage"> (-10%)
        block = re.sub(
            r'<span[^>]+class="[^"]*\bsale-percentage\b[^"]*"[^>]*>.*?</span>',
            '', block, flags=re.DOTALL | re.IGNORECASE
        )
        # Remove <span class="color-product-stock"> (empty stock label)
        block = re.sub(
            r'<span[^>]+class="[^"]*\bcolor-product-stock\b[^"]*"[^>]*>.*?</span>',
            '', block, flags=re.DOTALL | re.IGNORECASE
        )

        # Step 5: Extract the IDR value from the remaining plain text
        # At this point block should only contain "IDR 900.000" and whitespace
        price_match = re.search(r'IDR\s*([\d.]+)', block, re.IGNORECASE)
        if not price_match:
            print("  ⚠️  IDR price not found in product-price block.")
            print(f"     Remaining block: {block.strip()[:300]}")
            return None

        # Indonesian format: dots are thousand separators ("900.000" = 900,000)
        raw = price_match.group(1)            # e.g. "900.000"
        price_idr = int(raw.replace(".", "")) # -> 900000
        return price_idr

    except Exception as e:
        print(f"  ❌ Error fetching price: {e}")
        return None


def format_price(price: int) -> str:
    """Format integer to Indonesian Rupiah: 900000 -> 'IDR 900.000'"""
    return f"IDR {price:,}".replace(",", ".")


def send_ntfy(title: str, message: str, priority: str = "default", tags: list = None):
    """Send push notification via ntfy.sh."""
    if not NTFY_ENABLED:
        return
    try:
        headers = {"Title": title, "Priority": priority}
        if tags:
            headers["Tags"] = ",".join(tags)
        resp = requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=10
        )
        if resp.status_code == 200:
            print("  ✅ Ntfy notification sent!")
        else:
            print(f"  ⚠️  Ntfy error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"  ❌ Ntfy error: {e}")


def send_telegram(message: str):
    """Send message via Telegram bot."""
    if not TELEGRAM_ENABLED:
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            },
            timeout=10
        )
        if resp.status_code == 200:
            print("  ✅ Telegram message sent!")
        else:
            print(f"  ⚠️  Telegram error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"  ❌ Telegram error: {e}")


def notify_price_drop(price: int):
    """Alert: target price has been reached!"""
    now = datetime.now().strftime("%d %b %Y %H:%M WIB")

    send_ntfy(
        title="Melissa Price Alert!",
        message=(
            f"Target price reached!\n\n"
            f"{PRODUCT_NAME}\n"
            f"Current price: {format_price(price)}\n"
            f"Your target:   {format_price(TARGET_PRICE)}\n\n"
            f"{PRODUCT_URL}\n\n"
            f"Checked at {now}"
        ),
        priority="high",
        tags=["shopping_bags", "tada"]
    )

    send_telegram(
        f"<b>Melissa Price Alert!</b>\n\n"
        f"Target price reached!\n\n"
        f"<b>{PRODUCT_NAME}</b>\n"
        f"Current price: <b>{format_price(price)}</b>\n"
        f"Your target:   {format_price(TARGET_PRICE)}\n\n"
        f"<a href='{PRODUCT_URL}'>Buy now!</a>\n\n"
        f"Checked at {now}"
    )


def notify_hourly_update(price: int):
    """Regular update when price hasn't hit target yet."""
    SEND_HOURLY_UPDATES = True   # set False to only get notified on price drop
    if not SEND_HOURLY_UPDATES:
        return

    now = datetime.now().strftime("%d %b %Y %H:%M WIB")
    diff = price - TARGET_PRICE

    send_ntfy(
        title="Melissa Hourly Update",
        message=(
            f"{PRODUCT_NAME}\n"
            f"Current: {format_price(price)}\n"
            f"Target:  {format_price(TARGET_PRICE)}\n"
            f"Still {format_price(diff)} away\n\n"
            f"Checked at {now}"
        ),
        priority="low",
        tags=["mag"]
    )

    send_telegram(
        f"<b>Melissa Hourly Update</b>\n\n"
        f"<b>{PRODUCT_NAME}</b>\n"
        f"Current: {format_price(price)}\n"
        f"Target:  {format_price(TARGET_PRICE)}\n"
        f"Still <b>{format_price(diff)}</b> away\n\n"
        f"{now}"
    )


def run():
    print("Melissa Price Tracker started!")
    print(f"   Product : {PRODUCT_NAME}")
    print(f"   URL     : {PRODUCT_URL}")
    print(f"   Target  : {format_price(TARGET_PRICE)}")
    print(f"   Interval: every {CHECK_INTERVAL // 60} minutes\n")

    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] Checking price...")

        price = fetch_price()

        if price is None:
            print("  Could not get price, will retry next cycle.")
        else:
            print(f"  Current price: {format_price(price)}")
            print(f"  Target price:  {format_price(TARGET_PRICE)}")

            if price <= TARGET_PRICE:
                print("  TARGET REACHED! Sending alert...")
                notify_price_drop(price)
            else:
                print("  Not there yet. Sending hourly update...")
                notify_hourly_update(price)

        print(f"  Sleeping {CHECK_INTERVAL // 60} minutes...\n")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
