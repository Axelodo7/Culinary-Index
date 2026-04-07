# Deploy to Koyeb (Free, No Cold Starts)

## Steps

1. Go to [koyeb.com](https://koyeb.com) and sign up with GitHub
2. Click **Create Web Service**
3. Select **GitHub** → Choose `Axelodo7/Culinary-Index`
4. Koyeb auto-detects Python — just click **Deploy**
5. Your app will be live at `https://culinary-index-xxxxx.koyeb.app`

## After Deploy

Update the mobile app URL in `mobile/capacitor.config.json`:
```json
"server": {
  "url": "https://YOUR-KOYEB-URL.koyeb.app",
  ...
}
```

Then rebuild the APK:
```bash
cd mobile
npx cap sync android
cd android
.\gradlew.bat assembleDebug
```

## Why Koyeb?

- **Free tier** — no credit card needed
- **No cold starts** — "Light Sleep" wakes up in <1 second
- **No API restrictions** — scrapers work without issues
- **Auto-deploy** — pushes to GitHub trigger automatic redeploys
