# API Key Setup — Ad Copy Translator

The translator uses Claude AI from Anthropic to translate your ad headlines, body copy, and calls-to-action into Spanish and Portuguese. You need an API key to use it. Everything else in NewMarkets works without one.

---

## Step 1 — Create an Anthropic Account

1. Go to **https://console.anthropic.com/**
2. Click **Sign Up** and create an account (email + password)

## Step 2 — Add Billing

1. Once logged in, click **Settings** in the left sidebar
2. Click **Billing**
3. Add a credit card or payment method
4. Add credits — $5 is plenty to start, translation calls cost a few cents each

## Step 3 — Create an API Key

1. Click **API Keys** in the left sidebar
2. Click **Create Key**
3. Give it a name (e.g. "newmarkets")
4. Copy the key — it starts with `sk-ant-...`
5. Save it somewhere safe. You won't be able to see it again after you leave the page.

## Step 4 — Add the Key to NewMarkets

1. Open the folder where you saved `NewMarkets.exe`
2. Right-click in the folder > **New** > **Text Document**
3. Name it `.env` (delete the `.txt` part — Windows will warn you about changing the extension, click **Yes**)
4. Right-click the `.env` file > **Open with** > **Notepad**
5. Paste this single line, replacing the placeholder with your real key:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
6. Save and close Notepad

## Step 5 — Run NewMarkets

Double-click `NewMarkets.exe`. The translator page will now work. Go to **Translator** in the top navigation bar, pick a product, type your English ad copy, and click **Translate with Claude**.

---

## Troubleshooting

**"Translation failed. Check your API key."**
- Make sure the `.env` file is in the same folder as `NewMarkets.exe`
- Make sure the file is named exactly `.env` (not `.env.txt` — turn on "Show file extensions" in Windows Explorer to check)
- Make sure there are no spaces before or after the `=` sign
- Make sure you have credits on your Anthropic account

**Can't rename the file to `.env`**
- Open Notepad, paste the `ANTHROPIC_API_KEY=sk-ant-...` line, then go to **File > Save As**
- Change "Save as type" to **All Files**
- Type `.env` as the file name
- Save it in the same folder as `NewMarkets.exe`

**How much does it cost?**
- Each translation call costs about $0.01–0.03
- A full set (headline + body + CTA) runs about $0.05–0.10
- $5 in credits will get you hundreds of translations
