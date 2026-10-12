import os
import json
import hashlib
import requests
from urllib.parse import quote_plus

URL = "https://www.centralcoalfields.in/busns/all_notices.php"
BASE = "https://www.centralcoalfields.in/busns/"
SEEN_FILE = os.path.join(os.path.dirname(__file__), "seen.json")

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_seen(data):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_notices():
    # Site par AWS WAF challenge hai, isliye normal requests fail hota hai.
    # Playwright real browser se open karte hain.
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        pg = b.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36')
        pg.goto(URL, timeout=60000)
        pg.wait_for_timeout(8000)
        # table load hone ka wait
        try:
            pg.wait_for_selector("table", timeout=20000)
        except:
            pass
        html = pg.content()
        b.close()

    soup = BeautifulSoup(html, "lxml")
    notices = []
    for table in soup.find_all("table"):
        header = table.find("tr").get_text(" ", strip=True) if table.find("tr") else ""
        if "Reference Number" not in header:
            continue
        for tr in table.find_all("tr")[1:]:
            tds = tr.find_all(["td", "th"])
            if len(tds) < 9:
                continue
            cols = [td.get_text(" ", strip=True) for td in tds]
            if cols[0].lower().startswith("sl"):
                continue
            try:
                sl = cols[0]
                notice_dt = cols[1]
                auction_dt = cols[2]
                upload_dt = cols[3]
                qty = cols[4]
                category = cols[5]
                auction_by = cols[6]
                ref_no = cols[7]
                subject = cols[8]
                # file link
                link_tag = tds[-1].find("a", href=True)
                link = ""
                if link_tag:
                    href = link_tag["href"].strip()
                    link = href if href.startswith("http") else BASE + href.lstrip("/")

                if not ref_no and not subject:
                    continue
                uid = hashlib.md5(f"{ref_no}|{subject}".encode("utf-8")).hexdigest()
                notices.append({
                    "id": uid,
                    "sl": sl,
                    "notice_date": notice_dt,
                    "auction_date": auction_dt,
                    "upload_date": upload_dt,
                    "qty": qty,
                    "category": category,
                    "auction_by": auction_by,
                    "ref_no": ref_no,
                    "subject": subject,
                    "link": link
                })
            except Exception as e:
                print(f"row skip: {e}")
                continue
        if notices:
            break
    return notices

def send_whatsapp_callmebot(phone, apikey, message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={quote_plus(phone)}&text={quote_plus(message)}&apikey={quote_plus(apikey)}"
    r = requests.get(url, timeout=30)
    return r.status_code, r.text[:500]

def format_msg(n):
    return (
        f"🔔 CCL New Notice\n"
        f"Ref: {n['ref_no']}\n"
        f"Subject: {n['subject']}\n"
        f"Notice: {n['notice_date']} | Auction: {n['auction_date']} | Upload: {n['upload_date']}\n"
        f"Qty: {n['qty']} | {n['category']} | By: {n['auction_by']}\n"
        f"File: {n['link']}"
    )

def main():
    phone = os.environ.get("CALLMEBOT_PHONE", "").strip()
    apikey = os.environ.get("CALLMEBOT_APIKEY", "").strip()
    test_mode = os.environ.get("TEST_MODE", "") == "1"

    print(f"Fetching {URL} ...")
    notices = fetch_notices()
    print(f"Milne wale notices: {len(notices)}")
    if not notices:
        print("Koi notice parse nahi hua.")
        return

    seen = load_seen()
    if not seen:
        print("Pehli baar run: latest 5 ko seen mark kar rahe hain.")
        for n in notices[:5]:
            seen[n["id"]] = n
        save_seen(seen)
        print("Top 3 latest:")
        for n in notices[:3]:
            print(" -", n["ref_no"], "|", n["subject"])
        if test_mode and phone and apikey:
            code, resp = send_whatsapp_callmebot(phone, apikey, "✅ CCL Tracker active! Ab naya notice aate hi WhatsApp ayega.")
            print(f"Test msg: {code} {resp}")
        return

    new_list = [n for n in notices if n["id"] not in seen]
    print(f"Naye notices: {len(new_list)}")
    if not new_list:
        print("Kuch naya nahi hai.")
        return

    for n in reversed(new_list):
        msg = format_msg(n)
        print("NEW:", n["ref_no"], "|", n["subject"])
        if phone and apikey:
            try:
                code, resp = send_whatsapp_callmebot(phone, apikey, msg)
                print(f"WhatsApp sent: {code} {resp}")
            except Exception as e:
                print(f"WhatsApp fail: {e}")
        else:
            print(msg)
            print("--- PHONE/APIKEY set nahi hai, sirf print hua ---")
        seen[n["id"]] = n

    save_seen(seen)
    print("Done.")

if __name__ == "__main__":
    main()
