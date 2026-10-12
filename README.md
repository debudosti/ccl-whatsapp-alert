# CCL Notice -> Direct WhatsApp Alert (Free)

`https://www.centralcoalfields.in/busns/all_notices.php` par naya e-Auction / General Notice aate hi WhatsApp par message.

### Kaise kaam karta hai?
`ccl_check.py` har run me site ka table check karta hai -> `seen.json` se compare karta hai -> jo naya hota hai wahi WhatsApp bhejta hai.

### Setup - sirf 5 minute (Free, CallMeBot se)

**Step 1 - WhatsApp activate karo:**
1. Apne phone me contact save karo: `CallMeBot` - number `+34 644 71 27 53`
2. WhatsApp par usko ye message bhejo:
   ```
   I allow callmebot to send me messages
   ```
3. Turant tumko ek `apikey` milega (6 digit). Note kar lo.

**Step 2 - Script chalao:**
```bash
pip install -r requirements.txt

# Windows: set, Linux/Mac: export
export CALLMEBOT_PHONE=91XXXXXXXXXX
export CALLMEBOT_APIKEY=XXXXXX
python ccl_check.py
```
Pehli baar me purana spam nahi ayega, sirf latest 5 seen me save honge.
Dusri baar se naya notice = WhatsApp message.

Message aisa ayega:
```
🔔 CCL New Notice
Ref: 2807
Subject: Revised Notice Sale of Coal through Single Window...
Notice Date: 09/10/2026 | Auction: 14/10/2026
Link: https://www.centralcoalfields.in/...
```

### Automatic (bina PC chalaye) - GitHub Actions Free
1. Is folder ko GitHub repo me daalo
2. Repo Settings > Secrets > Actions me 2 secrets add karo:
   - `CALLMEBOT_PHONE` = 91XXXXXXXXXX
   - `CALLMEBOT_APIKEY` = tumhari key
3. `.github/workflows/check.yml` har 30 min me auto chalega
4. Naya notice = direct WhatsApp

### Bina coding chahiye?
- n8n / Zapier me RSS-by-scrape + WhatsApp node bhi lag sakta hai, par ye Python wala sabse sasta + reliable hai.

### Note
- CallMeBot sirf apne number par bhejta hai (spam rokne ke liye), jo is kaam ke liye perfect hai.
- Agar 2-3 logo ko bhejna hai to har number ko alag se activate karke script me loop laga dena.
